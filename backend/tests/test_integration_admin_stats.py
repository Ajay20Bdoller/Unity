def test_admin_stats_reflects_real_counts(admin_client, student_client):
    stats = admin_client.get("/admin/dashboard/stats").json()

    assert stats["total_users"] >= 2  # at least the admin + the student fixture created
    assert stats["users_by_role"]["student"] >= 1
    assert stats["users_by_role"]["admin"] >= 1
    assert stats["total_careers"] == 16  # seeded careers (4 original + 12 added later)
    assert stats["total_courses"] == 3  # seeded courses (1 original + 2 added later)
    assert any(u["full_name"] == "Role Matrix Student" for u in stats["recent_users"])


def test_non_admin_blocked_from_stats(student_client):
    res = student_client.get("/admin/dashboard/stats")
    assert res.status_code == 403
