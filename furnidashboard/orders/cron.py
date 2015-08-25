from orders.cron_tasks import unplaced_orders_notification, missed_orders_notification
import kronos

@kronos.register('0 7 * * 1,3,5')
def missed_orders_cron_task():
    missed_orders_notification.run_missed_orders_cron()

@kronos.register('0 6 * * 2,4')
def unplaced_orders_cron_task():
    unplaced_orders_notification.run_unplaced_orders_cron()

@kronos.register('30 6 * * 2,4')
def unplaced_orders_by_associate_cron_task():
    unplaced_orders_notification.run_unplaced_orders_by_assoc_cron()
