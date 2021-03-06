# Generated by Django 4.0.5 on 2022-06-09 12:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='list',
            name='order',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='task',
            name='order',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='list',
            name='board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lists', to='boards.board'),
        ),
        migrations.AlterField(
            model_name='task',
            name='list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='boards.list'),
        ),
    ]
