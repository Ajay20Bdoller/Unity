from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.deps import (
    require_admin,
    require_mentor,
    require_parent,
    require_school_admin,
    require_student,
)
from app.models.user import SELF_REGISTERABLE_ROLES, UserRole

_DEPENDENCY_BY_ROLE = {
    UserRole.STUDENT: require_student,
    UserRole.PARENT: require_parent,
    UserRole.MENTOR: require_mentor,
    UserRole.SCHOOL_ADMIN: require_school_admin,
    UserRole.ADMIN: require_admin,
}


def _user(role: UserRole) -> SimpleNamespace:
    return SimpleNamespace(role=role)


@pytest.mark.parametrize("allowed_role,dependency", _DEPENDENCY_BY_ROLE.items())
def test_require_role_allows_matching_role(allowed_role, dependency):
    user = _user(allowed_role)
    assert dependency(current_user=user) is user


@pytest.mark.parametrize("allowed_role,dependency", _DEPENDENCY_BY_ROLE.items())
def test_require_role_rejects_every_non_matching_role(allowed_role, dependency):
    for role in UserRole:
        if role is allowed_role:
            continue
        with pytest.raises(HTTPException) as exc_info:
            dependency(current_user=_user(role))
        assert exc_info.value.status_code == 403


def test_admin_is_not_self_registerable():
    assert UserRole.ADMIN not in SELF_REGISTERABLE_ROLES
    assert len(SELF_REGISTERABLE_ROLES) == 4
