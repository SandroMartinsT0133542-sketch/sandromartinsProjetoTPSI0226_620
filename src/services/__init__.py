"""Service package: business rules for record management and reporting."""

from .progress_service import (
	compute_statistics,
	create_record,
	delete_record,
	filter_weight_range,
	find_by_id,
	initialize_service,
	list_records,
	save_state,
	search_records,
	sort_records,
	update_record,
)

from .auth_service import (
	authenticate,
	current_user,
	current_user_id,
	initialize_auth,
	logout,
	register_user,
)

__all__ = [
	"initialize_service",
	"list_records",
	"create_record",
	"find_by_id",
	"update_record",
	"delete_record",
	"search_records",
	"sort_records",
	"compute_statistics",
	"filter_weight_range",
	"save_state",
	"initialize_auth",
	"authenticate",
	"current_user",
	"current_user_id",
	"logout",
	"register_user",
]
