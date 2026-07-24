from django.conf import settings
from django.core.mail import send_mail


def send_company_admin_invite(*, to: str, company_name: str, setup_url: str) -> dict:
    html_message = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #0f172a;">
          <h2>Your Bookutu dashboard access is ready</h2>
          <p>You have been invited as a company admin for <strong>{company_name}</strong>.</p>
          <p>Use the link below to set your password and finish your Bookutu account setup.</p>
          <p><a href="{setup_url}">{setup_url}</a></p>
        </div>
    """

    send_mail(
        subject=f'Set up your {company_name} Bookutu account',
        message=f'Set up your {company_name} Bookutu account: {setup_url}',
        html_message=html_message,
        from_email=settings.EMAIL_FROM_ADDRESS,
        recipient_list=[to],
        fail_silently=False,
    )

    mode = 'smtp' if settings.EMAIL_BACKEND.endswith('smtp.EmailBackend') else 'preview'
    return {'mode': mode}
