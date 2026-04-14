from flask import Blueprint, render_template
from services.reminder import ReminderService

reminder_bp = Blueprint('reminder', __name__)


@reminder_bp.route('/')
def index():
    pickup_reminders = ReminderService.get_pickup_reminders()
    payment_reminders = ReminderService.get_payment_reminders()
    return render_template('reminder/index.html',
                           pickup_reminders=pickup_reminders,
                           payment_reminders=payment_reminders)
