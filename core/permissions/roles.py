from core.domain.models.user import UserRole

MANAGE_PUBLISHERS_AND_PLACEMENTS = "manage_publishers_and_placements"
RUN_BID_SIMULATIONS = "run_bid_simulations"
VIEW_AUCTION_TRACES = "view_auction_traces"

ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.admin: {
        "manage_users",
        "manage_campaigns",
        MANAGE_PUBLISHERS_AND_PLACEMENTS,
        RUN_BID_SIMULATIONS,
        "run_bid_simulations",
        "log_events",
        "view_analytics",
        "use_copilot",
        VIEW_AUCTION_TRACES,
    },
    UserRole.adops: {
        "manage_campaigns",
        MANAGE_PUBLISHERS_AND_PLACEMENTS,
        RUN_BID_SIMULATIONS,
        "run_bid_simulations",
        "log_events",
        "view_analytics",
        "use_copilot",
        VIEW_AUCTION_TRACES,
    },
    UserRole.analyst: {
        "view_dashboard",
        VIEW_AUCTION_TRACES,
        "view_events",
        "use_copilot",
    },
    UserRole.viewer: {
        "view_dashboard",
        VIEW_AUCTION_TRACES,
    },
}
