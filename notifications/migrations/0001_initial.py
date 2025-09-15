
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0013_remove_employee_user'),  # Adjust this to your latest accounts migration
    ]

    operations = [
        migrations.CreateModel(
            name='PaycheckNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('paycheck', 'Paycheck Sent'), ('bonus', 'Bonus Payment'), ('salary_adjustment', 'Salary Adjustment')], default='paycheck', max_length=20)),
                ('message', models.TextField(default='Your paycheck has been sent!')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('sent_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_read', models.BooleanField(default=False)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paycheck_notifications', to='accounts.employee')),
                ('sent_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_notifications', to='accounts.employee')),
            ],
            options={
                'ordering': ['-sent_at'],
            },
        ),
    ]
