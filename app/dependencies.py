from fastapi import Header, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, UserRole
from app.database import get_db
import app.crud_user as crud_user
from app.security import decode_access_token

security = HTTPBearer()


async def get_current_user(
    credentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dépendance pour récupérer l'utilisateur courant via JWT token.
    Lève une exception 401 si le token est invalide.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No credentials provided"
        )
    
    token = credentials.credentials
    
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    try:
        user = await crud_user.get_user(user_id, db)
        return user
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )


def check_permission(current_user: User, resource_owner: User) -> bool:
    """
    Vérifie si l'utilisateur courant a la permission d'accéder à une ressource.
    
    Règles:
    - ADMIN : accès total
    - MODERATOR : accès sauf si la ressource appartient à un ADMIN
    - USER : accès seulement à ses propres ressources
    
    Lève une exception HTTP 403 si l'accès est refusé.
    """
    # ADMIN a tous les droits
    if current_user.role == UserRole.ADMIN:
        return True
    
    # MODERATOR peut tout sauf les ressources d'ADMIN
    if current_user.role == UserRole.MODERATOR:
        if resource_owner.role == UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Moderators cannot access admin resources"
            )
        return True
    
    # USER ne peut accéder qu'à ses propres ressources
    if current_user.role == UserRole.USER:
        if current_user.id != resource_owner.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own resources"
            )
        return True
    
    # Par défaut, refuser l'accès
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dépendance pour restreindre l'accès aux ADMIN uniquement.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_editor(current_user: User = Depends(get_current_user)) -> User:
    """Accès editor/admin (MODERATOR ou ADMIN)."""
    if current_user.role not in (UserRole.MODERATOR, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editor access required",
        )
    return current_user


def require_viewer(current_user: User = Depends(get_current_user)) -> User:
    """Accès viewer/editor/admin : tout utilisateur authentifié."""
    return current_user
