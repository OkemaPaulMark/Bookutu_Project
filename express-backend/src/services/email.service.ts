import nodemailer from 'nodemailer'
import { env } from '../config/env.js'

type CompanyAdminInviteEmail = {
  companyName: string
  setupUrl: string
  to: string
}

type EmailDeliveryResult =
  | { mode: 'preview' }
  | { mode: 'smtp', id: string }

const transporter = env.EMAIL_USER && env.EMAIL_PASSWORD
  ? nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: env.EMAIL_USER,
        pass: env.EMAIL_PASSWORD
      }
    })
  : null

function buildInviteHtml(payload: CompanyAdminInviteEmail) {
  return `
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #0f172a;">
      <h2 style="margin-bottom: 12px;">Your Bookutu dashboard access is ready</h2>
      <p>You have been invited as a company admin for <strong>${payload.companyName}</strong>.</p>
      <p>Use the button below to set your password and finish your Bookutu account setup.</p>
      <p style="margin: 24px 0;">
        <a href="${payload.setupUrl}" style="display: inline-block; background: #0f766e; color: white; padding: 12px 18px; border-radius: 10px; text-decoration: none;">
          Set Password
        </a>
      </p>
      <p>If the button does not work, open this link:</p>
      <p><a href="${payload.setupUrl}">${payload.setupUrl}</a></p>
    </div>
  `
}

async function sendWithSmtp(payload: CompanyAdminInviteEmail): Promise<EmailDeliveryResult> {
  if (!transporter || !env.EMAIL_USER) {
    console.info(`[email:preview] Company admin invite for ${payload.to}: ${payload.setupUrl}`)
    return { mode: 'preview' }
  }

  const info = await transporter.sendMail({
    from: env.EMAIL_FROM_ADDRESS ?? env.EMAIL_USER,
    to: payload.to,
    subject: `Set up your ${payload.companyName} Bookutu account`,
    html: buildInviteHtml(payload)
  })

  return {
    mode: 'smtp',
    id: info.messageId
  }
}

export const emailService = {
  async sendCompanyAdminInvite(payload: CompanyAdminInviteEmail) {
    return sendWithSmtp(payload)
  }
}
