# Generated by Django 5.2 on 2025-05-04 08:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('description', models.TextField()),
                ('starting_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('current_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('image', models.ImageField(upload_to='auction_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('end_date', models.DateTimeField()),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('PENDING', 'Pending Review'), ('CLOSED', 'Closed')], default='PENDING', max_length=10)),
                ('featured', models.BooleanField(default=False)),
                ('views_count', models.PositiveIntegerField(default=0)),
                ('is_notified', models.BooleanField(default=False)),
                ('is_paid', models.BooleanField(default=False)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auctions', to=settings.AUTH_USER_MODEL)),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='won_auctions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AuctionImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='auction_images/')),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='auctions.auction')),
            ],
        ),
        migrations.AddField(
            model_name='auction',
            name='additional_images',
            field=models.ManyToManyField(blank=True, related_name='auctions_as_additional', to='auctions.auctionimage'),
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='auctions.auction')),
                ('bidder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-amount'],
            },
        ),
        migrations.AddField(
            model_name='auction',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auctions', to='auctions.category'),
        ),
        migrations.CreateModel(
            name='EthAuction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_address', models.CharField(max_length=42)),
                ('contract_auction_id', models.PositiveIntegerField()),
                ('seller_address', models.CharField(max_length=42)),
                ('start_block', models.PositiveIntegerField()),
                ('end_block', models.PositiveIntegerField(blank=True, null=True)),
                ('last_sync_block', models.PositiveIntegerField()),
                ('auction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='eth_auction', to='auctions.auction')),
            ],
            options={
                'indexes': [models.Index(fields=['contract_address', 'contract_auction_id'], name='auctions_et_contrac_e95f3b_idx')],
            },
        ),
        migrations.CreateModel(
            name='EthBid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bidder_address', models.CharField(max_length=42)),
                ('amount_wei', models.CharField(max_length=78)),
                ('transaction_hash', models.CharField(max_length=66, unique=True)),
                ('block_number', models.PositiveIntegerField()),
                ('timestamp', models.DateTimeField()),
                ('eth_auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eth_bids', to='auctions.ethauction')),
            ],
            options={
                'ordering': ['-block_number'],
            },
        ),
        migrations.CreateModel(
            name='EthPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_address', models.CharField(max_length=42)),
                ('seller_address', models.CharField(max_length=42)),
                ('usd_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('eth_amount_wei', models.CharField(max_length=78)),
                ('tx_hash', models.CharField(max_length=66)),
                ('is_paid', models.BooleanField(default=False)),
                ('payment_time', models.DateTimeField(auto_now_add=True)),
                ('auction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ethpayment', to='auctions.auction')),
            ],
        ),
        migrations.CreateModel(
            name='Watchlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='watchlists', to='auctions.auction')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='watchlist', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='ethbid',
            index=models.Index(fields=['bidder_address'], name='auctions_et_bidder__04adee_idx'),
        ),
        migrations.AddIndex(
            model_name='ethbid',
            index=models.Index(fields=['transaction_hash'], name='auctions_et_transac_19b825_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='watchlist',
            unique_together={('user', 'auction')},
        ),
    ]
