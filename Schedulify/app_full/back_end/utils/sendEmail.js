import nodemailer from "nodemailer";
import ErrorHandler from "../middlewares/error.js";

export const sendEmail = async ({ email, subject, message }) => {
  if (!email || typeof email !== "string" || !email.includes("@")) {
    throw new ErrorHandler(400,"Invalid or missing recipient email address.");
  }

  try {
    console.log("📧 Preparing to send email to:", email);

    const transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: Number(process.env.SMTP_PORT) || 587,
      service: process.env.SMTP_SERVICE,
      auth: { 
        user: process.env.SMTP_MAIL,
        pass: process.env.SMTP_PASSWORD,
      },
    });

    const mailOptions = {
      from: `"Schedulify - system mail" <${process.env.SMTP_MAIL}>`,
      to: email,
      subject: subject,
      html: message,
    };

    const info = await transporter.sendMail(mailOptions);
    console.log("✅ Email sent successfully:", info.response);
  } catch (error) {
    console.error("❌ Failed to send email:", error.message);
    throw new ErrorHandler(400,"Email sending failed");
  }
};
