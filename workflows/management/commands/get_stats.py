from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from collections import defaultdict
from datetime import datetime


class Command(BaseCommand):
    help = 'Get some user usage stats'
    args = 'cut date'

    def diff_month(self, d1, d2):
    	year1 = int(d1.split('_')[0])
    	year2 = int(d2.split('_')[0])
    	month1 = int(d1.split('_')[1])
    	month2 = int(d2.split('_')[1])
        return (year1 - year2) * 12 + month1 - month2

    def format_date(self, num):
    	if num < 10:
    		num = str(0) + str(num)
    	else:
    		num = str(num)
    	return num

    def handle(self, *args, **options):
    	cut_date = args[0]
        users = User.objects.all()
        monthly_stats_joined = defaultdict(int)
        daily_stats_joined = defaultdict(int)
        monthly_stats_active = defaultdict(int)
        daily_stats_active = defaultdict(int)
        counter = 0
        today = str(datetime.today().year) + '_' + self.format_date(datetime.today().month) + '_' + self.format_date(datetime.today().day)
        all_months = self.diff_month(today, cut_date)


        for user in users:
      
        	ts_joined_d = str(user.date_joined.year) + '_' + self.format_date(user.date_joined.month) + '_' + self.format_date(user.date_joined.day)
        	ts_active_d = str(user.last_login.year) + '_' + self.format_date(user.last_login.month) + '_' + self.format_date(user.last_login.day)
        	ts_joined_m = str(user.date_joined.year) + '_' + self.format_date(user.date_joined.month)
        	ts_active_m = str(user.last_login.year) + '_' + self.format_date(user.last_login.month)

        	if ts_joined_m > cut_date:
        		counter += 1

        	monthly_stats_joined[ts_joined_m] += 1
        	monthly_stats_active[ts_active_m] += 1
        	daily_stats_joined[ts_joined_d] += 1
        	daily_stats_active[ts_active_d] += 1
        
        print 'New users per month: '
        
        for month, num in sorted(monthly_stats_joined.items(), key=lambda x:x[0]):
        	print month + ': ' + str(num)
        
        
        print 'New users since ', cut_date, ': ', counter
        print 'Average new users per month: ', counter/float(all_months)

   





        
