export function generateForgotPasswordEmailTemplate(resetPasswordUrl) {
  return `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8" />
        <title>Reset Password</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
          }
          .container {
            max-width: 600px;
            margin: 40px auto;
            background-color: #ffffff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
          }
          .header {
            text-align: center;
            color: #4A90E2;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
          }
          .message {
            font-size: 16px;
            color: #333333;
            line-height: 1.6;
          }
          .button {
            display: block;
            width: max-content;
            margin: 30px auto;
            padding: 12px 24px;
            background-color: #4A90E2;
            color: #ffffff;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
          }
          .footer {
            text-align: center;
            font-size: 12px;
            color: #999999;
            margin-top: 30px;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">Schedulify - the time table generator</div>
          <div class="message">
            <p>Hello,</p>
            <p>You recently requested to reset your password. Click the button below to reset it:</p>
            <a href="${resetPasswordUrl}" class="button">Reset Password</a>
            <p>If you did not request a password reset, please ignore this email.</p>
            <p>Thank you,<br/>Schedulify Team</p>
          </div>
          <div class="footer">
            &copy; ${new Date().getFullYear()} Schedulify. All rights reserved.
          </div>
        </div>
      </body>
    </html>
  `;
}
