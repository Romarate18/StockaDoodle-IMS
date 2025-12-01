from flask import Blueprint, request, jsonify
from extensions import db
from models.user import User
from models.retailer_metrics import RetailerMetrics
from core.sales_manager import SalesManager
from core.activity_logger import ActivityLogger

bp = Blueprint('metrics', __name__)


# ----------------------------------------------------------------------
# GET /api/v1/retailer/<user_id> → Get retailer metrics
# Returns: current_streak, daily_quota, sales_today, total_sales
# ----------------------------------------------------------------------
@bp.route('/<int:user_id>', methods=['GET'])
def get_retailer_metrics(user_id):
    """Get retailer's current performance metrics"""
    try:
        metrics = RetailerMetrics.query.filter_by(retailer_id=user_id).first()
        
        if not metrics:
            return jsonify({"errors": ["Retailer metrics not found"]}), 404
        
        return jsonify(metrics.to_dict()), 200
        
    except Exception as e:
        return jsonify({"errors": [f"Failed to get metrics: {str(e)}"]}), 500


# ----------------------------------------------------------------------
# GET /api/v1/retailer/leaderboard → Get top performing retailers
# Query params:
#   sort_by: String (optional) → 'daily_quota_usd' or 'current_streak'
#   limit: Integer (optional, default=10)
# ----------------------------------------------------------------------
@bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get top performing retailers"""
    try:
        sort_by = request.args.get('sort_by', 'current_streak')
        limit = request.args.get('limit', 10, type=int)
        
        if sort_by not in ['daily_quota_usd', 'current_streak', 'total_sales']:
            sort_by = 'current_streak'
        
        leaderboard = SalesManager.get_leaderboard(limit=limit)
        
        return jsonify({
            'leaderboard': leaderboard,
            'sort_by': sort_by,
            'total_retailers': len(leaderboard)
        }), 200
        
    except Exception as e:
        return jsonify({"errors": [f"Failed to get leaderboard: {str(e)}"]}), 500


# ----------------------------------------------------------------------
# PATCH /api/v1/retailer/<user_id>/quota → Update retailer daily quota
# Body:
#   daily_quota: Float (required) → New daily quota amount
#   updated_by: Integer (optional) → Admin/manager user ID
# ----------------------------------------------------------------------
@bp.route('/<int:user_id>/quota', methods=['PATCH'])
def update_retailer_quota(user_id):
    """Update retailer's daily quota"""
    data = request.get_json() or {}
    
    daily_quota = data.get('daily_quota')
    if daily_quota is None:
        return jsonify({"errors": ["daily_quota is required"]}), 400
    
    try:
        daily_quota = float(daily_quota)
        if daily_quota < 0:
            return jsonify({"errors": ["daily_quota must be non-negative"]}), 400
    except (TypeError, ValueError):
        return jsonify({"errors": ["daily_quota must be a number"]}), 400
    
    try:
        metrics = SalesManager.update_retailer_quota(user_id, daily_quota)
        
        # Log activity
        updated_by = data.get('updated_by')
        ActivityLogger.log_api_activity(
            method='PATCH',
            target_entity='retailer_metrics',
            user_id=updated_by,
            details=f"Updated quota for retailer {user_id} to ${daily_quota:.2f}"
        )
        
        return jsonify({
            'message': 'Quota updated successfully',
            'metrics': metrics.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"errors": [str(e)]}), 400


# ----------------------------------------------------------------------
# POST /api/v1/retailer/<user_id>/reset-streak → Reset retailer streak
# Body:
#   admin_id: Integer (optional) → Admin performing the reset
# ----------------------------------------------------------------------
@bp.route('/<int:user_id>/reset-streak', methods=['POST'])
def reset_retailer_streak(user_id):
    """Reset retailer's streak (admin/manager only)"""
    data = request.get_json() or {}
    
    try:
        metrics = RetailerMetrics.query.filter_by(retailer_id=user_id).first()
        if not metrics:
            return jsonify({"errors": ["Retailer metrics not found"]}), 404
        
        old_streak = metrics.current_streak
        metrics.current_streak = 0
        db.session.commit()
        
        # Log activity
        admin_id = data.get('admin_id')
        ActivityLogger.log_api_activity(
            method='POST',
            target_entity='retailer_metrics',
            user_id=admin_id,
            details=f"Reset streak for retailer {user_id} (was {old_streak})"
        )
        
        return jsonify({
            'message': 'Streak reset successfully',
            'previous_streak': old_streak,
            'current_streak': 0
        }), 200
        
    except Exception as e:
        return jsonify({"errors": [f"Failed to reset streak: {str(e)}"]}), 500