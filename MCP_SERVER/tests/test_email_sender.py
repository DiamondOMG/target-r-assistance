import unittest
from unittest.mock import MagicMock, patch
from jarvis_mcp.email_sender import send_email


class TestEmailSender(unittest.TestCase):
    @patch("smtplib.SMTP_SSL")
    def test_send_email_success_plain(self, mock_smtp_ssl):
        mock_server = MagicMock()
        mock_smtp_ssl.return_value.__enter__.return_value = mock_server

        res = send_email(
            to=["test@example.com"],
            subject="Test Subject",
            body="Hello World",
            user="sender@gmail.com",
            password="mockpassword1234",
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["to"], ["test@example.com"])
        self.assertEqual(res["subject"], "Test Subject")
        mock_server.login.assert_called_once_with("sender@gmail.com", "mockpassword1234")
        mock_server.sendmail.assert_called_once()

    @patch("smtplib.SMTP_SSL")
    def test_send_email_success_html(self, mock_smtp_ssl):
        mock_server = MagicMock()
        mock_smtp_ssl.return_value.__enter__.return_value = mock_server

        res = send_email(
            to="recipient1@example.com, recipient2@example.com",
            subject="HTML Report",
            body="<h1>Heading</h1><p>Content</p>",
            is_html=True,
            cc=["manager@example.com"],
            user="sender@gmail.com",
            password="mockpassword1234",
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["to"]), 2)
        self.assertEqual(res["cc"], ["manager@example.com"])
        self.assertTrue(res["is_html"])

    def test_missing_credentials_raises(self):
        with self.assertRaises(ValueError):
            send_email(to=["test@example.com"], subject="Hi", body="Text", user="", password="")

    def test_missing_recipient_raises(self):
        with self.assertRaises(ValueError):
            send_email(to="", subject="Hi", body="Text", user="a@b.com", password="pwd")


if __name__ == "__main__":
    unittest.main()

