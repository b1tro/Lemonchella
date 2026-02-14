import gspread

from models import Order
import config

from gspread_formatting import CellFormat, Color, format_cell_range
from gspread.utils import rowcol_to_a1
from bot import callbacks
import datetime


class GoogleSheets:

    def __init__(self, service_key_path: str):
        self.gs = gspread.service_account(filename=service_key_path)

    def get_sheet(self, sheet_url: str, range='all'):
        sheet = self.gs.open_by_url(sheet_url).sheet1
        sheet.sort((1, 'des'), (13, 'des'))

        if range == 'all':
            return sheet.get_all_values()
        else:
            return sheet.get(range)

    def add_row(self, sheet_url: str, row: tuple[str, ...]):
        sheet = self.gs.open_by_url(sheet_url).sheet1
        sheet.append_row(values=row)
        sheet.sort((1, 'des'), (9, 'des'))

    def add_order(self, sheet_url: str, order: Order, buyer_username: str = None, product_name: str = None):
        payments = order.payment.model_dump_json() if order.payment else ''
        if payments and order.balance_payment:
            payments += ' + '
        payments += order.balance_payment.model_dump_json() if order.balance_payment else ''
        products = ', '.join([str(i) for i in order.order_items])

        row = (
            order.status,
            f'{order.id}',
            f'@{buyer_username} ({order.user_id})',
            getattr(order, 'telegram_chat_link', ''),
            products,
            f'{order.total}',
            f'{order.balance_payment.amount}' if order.balance_payment else '',
            payments,
            order.created_at.strftime('%d.%m.%Y %H:%M:%S'),
            order.referrer_id if order.referrer_id else '',
            order.referral_amount if order.referral_amount else ''
        )
        return self.add_row(sheet_url=sheet_url, row=row)

    def get_orders(self, sheet_url: str):
        orders_sheet = self.get_sheet(sheet_url=sheet_url)
        active_orders = [
            row for row in orders_sheet
            if len(row) >= 11
        ]
        return active_orders

    def create_order_table(self, order: Order, buyer_username: str = None) -> str:
        source_sheet = self.gs.open_by_url(config.DUPLICATE_SPREADSHEET_URL)

        spreadsheet_copy = self.gs.copy(
            file_id=source_sheet.id,
            title=f'#order {order.pid}'
        )

        spreadsheet_copy.share('anyone', 'anyone', 'writer')

        return spreadsheet_copy.url

    def find_row_by_order_id(self, gid: int, order: Order):
        spreadsheet = self.gs.open_by_url(
            config.SUMMARY_SHEET_URL if not order.is_special else config.SPECIAL_SHEET_URL)
        worksheet = spreadsheet.get_worksheet_by_id(gid)
        rows = worksheet.get_all_values()
        for i, row in enumerate(rows, start=1):
            if row[1] == f'#{order.pid}':
                return i
        return -1

    def update_google_sheets(self, order: Order, gid: int, username: str, customer: str, referral: str = None,
                             exact_row: int = -1):
        spreadsheet = self.gs.open_by_url(
            config.SUMMARY_SHEET_URL if not order.is_special else config.SPECIAL_SHEET_URL)
        worksheet = spreadsheet.get_worksheet_by_id(gid)
        if worksheet is None:
            raise ValueError(f"Лист с gid={gid} не найден в таблице.")

        if exact_row == -1:
            all_values = worksheet.get_all_values()
            next_row = len(all_values) + 1
        else:
            next_row = exact_row

        diff_formula = f'=E{next_row}-F{next_row}'

        print(order)

        if not order.is_special:
            row = (
                datetime.datetime.now().strftime("%d.%m.%y"),
                f'#{order.pid}',
                f'@{username}',
                f'{order.order_items[0].quantity}x {order.order_items[0].product_name}',
                str(round(float(order.total), 2)).replace('.', ','),
                str(round(float(order.total_customer), 2)).replace('.',
                                                                   ',') if order.complete_status != callbacks.COMPLETE_FAILED else str(
                    round(float(order.total), 2)).replace('.', ','),
                diff_formula,
                f'@{customer}',
                f'@{referral}' if referral else ''
            )
        else:
            row = (
                datetime.datetime.now().strftime("%d.%m.%y"),
                f'#{order.pid}',
                f'@{username}',
                f'{order.order_items[0].quantity}x {order.order_items[0].product_name}',
                str(round(float(order.total_summary), 2)).replace('.', ','),
                str(round(float(order.total_customer_summary), 2)).replace('.',
                                                                           ',') if order.complete_status != callbacks.COMPLETE_FAILED else str(
                    round(float(order.total_summary), 2)).replace('.', ','),
                diff_formula,
                f'@{customer}',
                f'@{referral}' if referral else ''
            )

        if exact_row == -1:
            worksheet.append_row(
                values=row,
                value_input_option='USER_ENTERED'
            )
        else:
            start_cell = rowcol_to_a1(exact_row, 1)
            end_cell = rowcol_to_a1(exact_row, len(row))
            range_ = f"{start_cell}:{end_cell}"
            worksheet.update(range_, [list(row)], value_input_option='USER_ENTERED')

            if order.complete_status != '':
                colors = {
                    callbacks.COMPLETE_FULL: Color(red=0.17, green=0.60, blue=0.25),
                    callbacks.COMPLETE_PART: Color(red=1, green=0.87, blue=0.52),
                    callbacks.COMPLETE_FAILED: Color(red=0.88, green=0.51, blue=0.52),
                }

                cell_format = CellFormat(
                    backgroundColor=colors[order.complete_status]
                )
                format_cell_range(worksheet, range_, cell_format)
            elif order.status == 'Deleted':
                cell_format = CellFormat(
                    backgroundColor=Color(red=0.51, green=0.57, blue=0.92)
                )
                format_cell_range(worksheet, range_, cell_format)

        worksheet.sort((2, 'des'))
