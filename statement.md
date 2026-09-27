# Project Statement

## Project title

Age Calculator Web Application

## Problem

People often need an exact age calculation for forms, planning, birthdays, and personal records. Manual date subtraction is error-prone, especially around month lengths, leap years, and dates near a birthday.

## Proposed solution

This project provides a browser-based calculator backed by Flask. Users enter a name, date of birth, and reference date. The application validates the dates, calculates an exact age, presents useful totals, stores recent calculations locally, and exports a readable report.

## Objectives

1. Accept dates in the user-friendly `dd/mm/yyyy` format.
2. Reject incomplete, impossible, or incorrectly ordered dates.
3. Calculate years, months, days, and elapsed time totals.
4. Predict a broad age group using a supervised AIML classifier.
5. Show the next birthday and weekday information.
6. Allow users to review recent calculations.
7. Produce PDF, Excel, Word, and text reports.
8. Provide automated tests for core behavior and error handling.

## Scope

The application is designed for individual calculations in a web browser. History is local to the browser and is limited to the ten most recent successful calculations. It does not provide accounts, cloud synchronization, or shared records.

## Target users

- Students demonstrating a date-processing web application.
- Individuals checking age for forms, planning, or personal records.
- Developers who need a small example of Flask, browser validation, and report export.

## High-level features

- Date entry with `dd/mm/yyyy` formatting and calendar selection.
- Exact age and elapsed-time calculations.
- Supervised age-group prediction: Child, Teenager, Adult, or Senior.
- Birthday information and next-birthday calculation.
- Local recent-history review and restoration.
- PDF, Excel, Word, and text-table reporting.
- Client-side and server-side validation with automated tests.

## Success criteria

The project is successful when valid calculations produce consistent results across the UI and exports, invalid input receives a clear response, history can restore a previous calculation, and the automated test suite passes.
