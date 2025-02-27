# ©  2015-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo.tests import Form, tagged

from .common import TestPaymenttoStatement


@tagged("post_install", "-at_install")
class TestPayment(TestPaymenttoStatement):
    def setUp(self):
        super(TestPayment, self).setUp()
        self.env.company.l10n_ro_accounting = True
        self.partner_a = self.env["res.partner"].create({"name": "test"})

    def test_payment(self):

        cash_journal = self.env["account.journal"].search(
            [("type", "=", "cash")], limit=1
        )

        payment_1 = self.env["account.payment"].create(
            {
                "amount": 150.0,
                "payment_type": "inbound",
                "partner_type": "customer",
                "date": "2015-01-01",
                "journal_id": cash_journal.id,
                "partner_id": self.partner_a.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )

        payment_2 = self.env["account.payment"].create(
            {
                "amount": 250.0,
                "payment_type": "outbound",
                "partner_type": "supplier",
                "date": "2015-01-02",
                "journal_id": cash_journal.id,
                "partner_id": self.partner_a.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
            }
        )

        payment_3 = self.env["account.payment"].create(
            {
                "amount": 250.0,
                "payment_type": "outbound",
                "partner_type": "customer",
                "date": "2015-01-02",
                "journal_id": cash_journal.id,
                "partner_id": self.partner_a.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
            }
        )

        payment_1.action_post()
        payment_2.action_post()
        payment_3.action_post()

        dashboard_data = cash_journal.get_journal_dashboard_datas()
        # self.assertEqual(dashboard_data["number_draft"], 0)
        # self.assertIn("0.00", dashboard_data["sum_draft"])
        # self.assertIn("-350.00", dashboard_data["outstanding_pay_account_balance"])
        self.assertIn(
            "-\ufeff350.00\xa0lei", dashboard_data["outstanding_pay_account_balance"]
        )

    def test_payment_date_journal(self):
        cash_journal = self.env["account.journal"].search(
            [("type", "=", "cash")], limit=1
        )
        payment_4 = self.env["account.payment"].create(
            {
                "amount": 150.0,
                "payment_type": "inbound",
                "partner_type": "customer",
                "date": "2015-02-02",
                "journal_id": cash_journal.id,
                "partner_id": self.partner_a.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )
        payment_form = Form(payment_4)
        payment_form.date = "2015-02-02"

    def test_payment_cash_in_journal(self):
        cash_journal = self.env["account.journal"].search(
            [("type", "=", "cash"), ("company_id", "=", self.env.company.id)], limit=1
        )
        moves = self.env["account.move"].search([])
        moves.unlink()
        payment_5 = self.env["account.payment"].create(
            {
                "amount": 150.0,
                "payment_type": "inbound",
                "partner_type": "customer",
                "date": "2022-12-01",
                "journal_id": cash_journal.id,
                "partner_id": self.partner_a.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )
        payment_5.action_post()
        self.assertEqual(payment_5.name, cash_journal.code + "CH-000001")

    def test_payment_cash_out_journal(self):
        cash_journal = self.env["account.journal"].search(
            [("type", "=", "cash"), ("company_id", "=", self.env.company.id)], limit=1
        )
        payment_6 = self.env["account.payment"].create(
            {
                "amount": 150.0,
                "payment_type": "outbound",
                "partner_type": "customer",
                "date": "2022-12-01",
                "journal_id": cash_journal.id,
                "partner_id": self.partner_a.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "company_id": self.env.company.id,
            }
        )
        payment_6.action_post()
        self.assertEqual(payment_6.name, cash_journal.code + "DP-000001")

    def test_payment_supplier_cash_out_journal(self):
        cash_journal = self.env["account.journal"].search(
            [("type", "=", "cash"), ("company_id", "=", self.env.company.id)], limit=1
        )
        # import ipdb; ipdb.set_trace()
        moves = self.env["account.move"].search([])
        moves.unlink()
        payment_7 = self.env["account.payment"].create(
            {
                "amount": 150.0,
                "payment_type": "outbound",
                "partner_type": "supplier",
                "date": "2022-12-01",
                "journal_id": cash_journal.id,
                "partner_id": self.partner_a.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "company_id": self.env.company.id,
            }
        )
        payment_7.action_post()
        self.assertEqual(payment_7.name, cash_journal.code + "-000001")

        vals_seq = {
            "name": "Seq",
            "code": "TT",
            "implementation": "no_gap",
            "prefix": "TT",
            "suffix": "",
            "padding": 6,
            "company_id": self.env.company.id,
        }
        seq = self.env["ir.sequence"].create(vals_seq)
        cash_journal.l10n_ro_journal_sequence_id = seq.id
        payment_8 = self.env["account.payment"].create(
            {
                "amount": 150.0,
                "payment_type": "outbound",
                "partner_type": "supplier",
                "date": "2022-12-01",
                "journal_id": cash_journal.id,
                "partner_id": self.partner_a.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "company_id": self.env.company.id,
            }
        )
        payment_8.action_post()
        self.assertEqual(payment_8.name, "TT000001")

    def test_bank_statement_line_name(self):
        bnk_line_out = self.env["account.bank.statement.line"].create(
            {
                "date": "2022-12-01",
                "payment_ref": "line_1",
                "amount": 100.0,
                "journal_id": self.company_data["default_journal_cash"].id,
            }
        )
        self.assertEqual(bnk_line_out.move_id.name, "CSH1-000001")

    def test_get_journal_dashboard_datas(self):
        payment_debit_account_id = self.env.company.transfer_account_id
        self.env.company.account_journal_payment_debit_account_id = (
            payment_debit_account_id
        )
        # account_type = (
        #     self.env["account.account.type"]
        #     .search([("name", "=", "Current Assets")])
        #     .id
        # )
        journal = self.env["account.journal"].create(
            {
                "name": "Test cash",
                "type": "cash",
                "company_id": self.env.company.id,
            }
        )
        payment = self.env["account.payment"].create(
            {
                "amount": 150.43,
                "payment_type": "inbound",
                "partner_type": "customer",
                "date": "2015-01-01",
                "journal_id": journal.id,
                "partner_id": self.partner_a.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )
        payment.action_post()
        dashboard_data = journal.get_journal_dashboard_datas()
        # self.assertEqual(dashboard_data["number_draft"], 0)
        # self.assertIn("0.00", dashboard_data["sum_draft"])
        self.assertIn("150.43", dashboard_data["outstanding_pay_account_balance"])
        self.assertEqual(dashboard_data["nb_lines_outstanding_pay_account_balance"], 1)

    def test_add_statement_line(self):

        journal = self.env["account.journal"].create(
            {
                "name": "Test cash",
                "type": "cash",
                "company_id": self.env.company.id,
                "l10n_ro_auto_statement": True,
            }
        )
        payment = self.env["account.payment"].create(
            {
                "amount": 111.50,
                "payment_type": "inbound",
                "partner_type": "customer",
                "date": "2015-01-01",
                "journal_id": journal.id,
                "partner_id": self.partner_a.id,
            }
        )
        payment.action_post()
        created_statement = self.env["account.bank.statement"].search(
            [("date", "=", "2015-01-01")]
        )
        self.assertEqual(created_statement.journal_id, journal)
        self.assertEqual(created_statement.balance_end, 111.5)
        self.assertEqual(created_statement.balance_end_real, 111.5)
        payment.action_draft()
        self.assertEqual(created_statement.balance_end, 0.0)
        created_statement._compute_balance_end_real()
        self.assertEqual(created_statement.balance_end_real, 0.0)
