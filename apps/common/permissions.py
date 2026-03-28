"""
Custom permission classes for the KCK API.

The KCK leadership has a role hierarchy: Chairman > Secretary/Treasurer/Welfare/Committee.
Each role maps to specific permission flags stored in the LeaderPermission model. The
chairman implicitly inherits ALL permissions because the chairman role is included in
every permission class's fallback role list.

I designed a two-tier permission check: first we look at explicit permission flags in
LeaderPermission (which the chairman can customize per-leader), then fall back to the
default role-based check. This lets the chairman grant, say, a committee member the
ability to manage users without changing their role -- useful for temporary delegation.

The IsOwnerOrSecretary class demonstrates object-level permissions: a user can view/edit
their own profile, but only the secretary or chairman can view/edit other users' profiles.
This pattern keeps member data private while still allowing leadership to administer accounts.

Author: Meshack Tirop (Tirop Meshack Kimutai)
"""
from rest_framework.permissions import BasePermission


def _get_leader(user):
    """Return the active Leader record for a user, or None."""
    if not user or not user.is_authenticated:
        return None
    try:
        leader = user.leader
        if leader.is_active:
            return leader
    except Exception:
        pass
    return None


def _has_permission_flag(leader, flag_name):
    """
    Check if a leader has a specific permission flag set to True.
    Returns True if the flag is True, False if it's False.
    Returns None if no LeaderPermission record exists (caller should fall back to role check).
    """
    try:
        perms = leader.permissions
        return getattr(perms, flag_name, None)
    except Exception:
        return None


class IsChairman(BasePermission):
    """
    Only the active chairman, or a leader explicitly granted can_manage_leaders.
    The chairman inherits all permissions by virtue of their role being checked first
    in every permission class. This is the most restrictive permission -- used for
    sensitive operations like deleting users and managing the leadership roster.
    """

    def has_permission(self, request, view):
        leader = _get_leader(request.user)
        if leader is None:
            return False
        if leader.role == "chairman":
            return True
        flag = _has_permission_flag(leader, "can_manage_leaders")
        if flag is not None:
            return flag
        return False


class IsSecretary(BasePermission):
    """Chairman or active secretary — checks can_manage_users permission flag."""

    def has_permission(self, request, view):
        leader = _get_leader(request.user)
        if leader is None:
            return False
        # Check permission flag first
        flag = _has_permission_flag(leader, "can_manage_users")
        if flag is not None:
            return flag
        # Fallback to role check
        return leader.role in ("chairman", "secretary")


class IsTreasurer(BasePermission):
    """Chairman or active treasurer — checks can_manage_memberships permission flag."""

    def has_permission(self, request, view):
        leader = _get_leader(request.user)
        if leader is None:
            return False
        flag = _has_permission_flag(leader, "can_manage_memberships")
        if flag is not None:
            return flag
        return leader.role in ("chairman", "treasurer")


class IsWelfare(BasePermission):
    """Chairman or active welfare officer — checks can_issue_certificates permission flag."""

    def has_permission(self, request, view):
        leader = _get_leader(request.user)
        if leader is None:
            return False
        flag = _has_permission_flag(leader, "can_issue_certificates")
        if flag is not None:
            return flag
        return leader.role in ("chairman", "welfare")


class IsCommittee(BasePermission):
    """Chairman or active committee member — checks can_manage_events permission flag."""

    def has_permission(self, request, view):
        leader = _get_leader(request.user)
        if leader is None:
            return False
        flag = _has_permission_flag(leader, "can_manage_events")
        if flag is not None:
            return flag
        return leader.role in ("chairman", "committee")


class IsAnyLeader(BasePermission):
    """Any user with an active leader record."""

    def has_permission(self, request, view):
        return _get_leader(request.user) is not None


class IsOwnerOrSecretary(BasePermission):
    """
    Object-level permission: the user owns the object OR the user is secretary/chairman.

    This is the core pattern for user profile access. has_permission() is intentionally
    permissive (any authenticated user passes) because the real check happens in
    has_object_permission() where we compare the requesting user's ID against the
    object's ID. This two-step approach is required by DRF -- has_permission runs
    before the object is loaded, has_object_permission runs after.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.id == obj.id:
            return True
        leader = _get_leader(request.user)
        if leader is None:
            return False
        flag = _has_permission_flag(leader, "can_manage_users")
        if flag is not None:
            return flag
        return leader.role in ("chairman", "secretary")
