from core.domain.models.user import UserRole

MANAGE_PUBLISHERS_AND_PLACEMENTS = "manage_publishers_and_placements"

ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.admin: {
        "manage_users",
        "manage_campaigns",
        MANAGE_PUBLISHERS_AND_PLACEMENTS,
        "run_bid_simulations",
        "log_events",
        "view_analytics",
        "use_copilot",
    },
    UserRole.adops: {
        "manage_campaigns",
        MANAGE_PUBLISHERS_AND_PLACEMENTS,
        "run_bid_simulations",
        "log_events",
        "view_analytics",
        "use_copilot",
    },
    UserRole.analyst: {
        "view_dashboard",
        "view_auction_traces",
        "view_events",
        "use_copilot",
    },
    UserRole.viewer: {
        "view_dashboard",
        "view_auction_traces",
    },
}
