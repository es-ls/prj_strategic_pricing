from __future__ import annotations

import argparse

from strategic_pricing_calculator.calculator import calculate_pricing
from strategic_pricing_calculator.workbook import (
    create_template_workbook,
    read_input_workbook,
    write_result_workbook,
)


def calculate_command() -> None:
    parser = argparse.ArgumentParser(description="Calculate strategic project pricing from Excel.")
    parser.add_argument("input", help="Input Excel workbook path")
    parser.add_argument("output", help="Output Excel workbook path")
    args = parser.parse_args()

    input_data = read_input_workbook(args.input)
    result = calculate_pricing(input_data)
    write_result_workbook(args.output, input_data, result)
    print(f"Wrote pricing result to {args.output}")


def template_command() -> None:
    parser = argparse.ArgumentParser(description="Create a sample strategic pricing input workbook.")
    parser.add_argument("output", help="Template Excel workbook path")
    args = parser.parse_args()

    create_template_workbook(args.output)
    print(f"Wrote template workbook to {args.output}")
