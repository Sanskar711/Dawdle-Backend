from django.db import migrations

def copy_m2m_data(apps, schema_editor):
    Meeting = apps.get_model('clients', 'Meeting')
    MeetingQualifyingQuestionResponse = apps.get_model('clients', 'MeetingQualifyingQuestionResponse')

    for meeting in Meeting.objects.all():
        m2m_links = MeetingQualifyingQuestionResponse.objects.filter(meeting=meeting)
        for link in m2m_links:
            meeting.qualifying_question_responses_temp.add(link.qualifying_question_response)

class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunPython(copy_m2m_data),
    ]
