# Generated by Django 3.2.25 on 2025-02-20 07:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('doctors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionSite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('mrn', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True, verbose_name='Medical Record Number')),
                ('first_name', models.CharField(max_length=255, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=255, verbose_name='Last Name')),
                ('dob', models.DateField(verbose_name='Date of Birth')),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('U', 'Unknown')], max_length=20, verbose_name='Gender')),
                ('phone', models.CharField(blank=True, max_length=255, null=True, verbose_name='Phone Number')),
                ('email', models.CharField(blank=True, max_length=255, null=True, verbose_name='Email Address')),
                ('address', models.TextField(blank=True, null=True, verbose_name='Address')),
            ],
        ),
        migrations.CreateModel(
            name='Specimen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specimen_type', models.CharField(choices=[('Blood', 'Blood'), ('Urine', 'Urine'), ('Tissue', 'Tissue'), ('Swab', 'Swab'), ('Fluids', 'Fluids'), ('FNA Sample', 'FNA Sample'), ('Other', 'Other')], max_length=255, verbose_name='Specimen Type')),
                ('collection_date_time', models.DateTimeField(verbose_name='Collection Date and Time')),
                ('received_date_time', models.DateTimeField(verbose_name='Received Date and Time')),
                ('quantity', models.CharField(blank=True, max_length=255, null=True, verbose_name='Quantity')),
                ('condition', models.CharField(blank=True, max_length=255, null=True, verbose_name='Condition')),
                ('collection_site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='patients.collectionsite', verbose_name='Collection Site')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specimens', to='patients.patient', verbose_name='Patient')),
            ],
            options={
                'db_table': 'patients_specimen',
            },
        ),
        migrations.CreateModel(
            name='TestOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_name', models.CharField(choices=[('histology', 'Histology'), ('cytology', 'Cytology'), ('pbf', 'Peripheral Blood Film'), ('immunohistochemistry', 'immunohistochemistry')], max_length=255, verbose_name='Test Type')),
                ('order_date_time', models.DateTimeField(auto_now_add=True, verbose_name='Order Date and Time')),
                ('ordering_doctor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='doctors.doctor')),
                ('specimen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_orders', to='patients.specimen', verbose_name='Specimen')),
            ],
        ),
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result_order_date_time', models.DateTimeField(blank=True, null=True, verbose_name='Order Date and Time')),
                ('nature_of_specimen', models.TextField(verbose_name='Nature of Specimen')),
                ('clinical_history', models.TextField(verbose_name='Clinical History')),
                ('macroscopy_description', models.TextField(verbose_name='Macroscopic Description')),
                ('microscopy_description', models.TextField(verbose_name='Microscopic Description')),
                ('diagnosis', models.TextField(blank=True, null=True)),
                ('test_order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='test_result', to='patients.testorder', verbose_name='Test Order')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comments_conclusion', models.TextField(verbose_name='Comments and Conclusion')),
                ('doctor_signature', models.CharField(blank=True, max_length=255, null=True, verbose_name="Doctor's Signature")),
                ('report_generated_date_time', models.DateTimeField(auto_now_add=True, verbose_name='Report Generated Date and Time')),
                ('report_verified_date_time', models.DateTimeField(blank=True, null=True, verbose_name='Report Verified Date and Time')),
                ('test_order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='report', to='patients.testorder', verbose_name='Test Order')),
            ],
        ),
    ]
