#!/usr/bin/env python
# Simple script for backuping single file
# https://github.com/xkrt/bckpr

from datetime import datetime
import glob
import os
import shutil
import sys
import smtplib
from email.mime.text import MIMEText
import platform

########################################
# Configuration
TargetFilePath = "/path/to/target/file"
BackupDirPath = "/path/to/backup-dir/"

WeeklyBackupDay = 1   # 0 - Monday .. 6 - Sunday
MonthlyBackupDay = 1  # day of month

KeepDailyBackupsForDays = 2
KeepWeeklyBackupsForDays = 14
KeepMonthlyBackupsForDays = 60

SmtpServer = "mail.server"
FromMail = "from@example.com"
ToMail = ["to@example.com"]
########################################

today = datetime.now().date()
todaystr = today.strftime("%Y%m%d")
target_fname = os.path.basename(TargetFilePath)


def check_pathes_exists():
    if not os.path.isfile(TargetFilePath):
        raise Exception("Cant find target file " + TargetFilePath)
    if not os.path.isdir(BackupDirPath):
        raise Exception("Cant find backup dir " + BackupDirPath)


def copy_to_backup(backup_fname):
    backup_fpath = os.path.join(BackupDirPath, backup_fname)
    shutil.copy(TargetFilePath, backup_fpath)


def remove_old_backups(globmask, keep_for_days):
    search_path = os.path.join(BackupDirPath, globmask)
    files = [x for x in glob.glob(search_path) if os.path.isfile(x)]

    for fpath in files:
        creation_date = datetime.fromtimestamp(os.path.getmtime(fpath)).date()
        delta = today - creation_date
        if delta.days >= keep_for_days:
            os.remove(fpath)


def daily_backup():
    backup_fname = target_fname + "_" + todaystr + "_daily"
    copy_to_backup(backup_fname)
    remove_old_backups("*_daily", KeepDailyBackupsForDays)


def weekly_backup():
    if today.weekday() != WeeklyBackupDay:
        return
    backup_fname = target_fname + "_" + todaystr + "_weekly"
    copy_to_backup(backup_fname)
    remove_old_backups("*_weekly", KeepWeeklyBackupsForDays)


def monthly_backup():
    if today.day != MonthlyBackupDay:
        return
    backup_fname = target_fname + "_" + todaystr + "_monthly"
    copy_to_backup(backup_fname)
    remove_old_backups("*_monthly", KeepMonthlyBackupsForDays)


def report_error(err):
    msg = "Error occurs while creating backup of " + TargetFilePath + "\n" \
          + "Host: " + platform.node() + "\n" \
          + "Target file path: " + TargetFilePath + "\n" \
          + "Backup dir path: " + BackupDirPath + "\n" \
          + "Error: " + str(err)

    msg = MIMEText(msg)
    msg["Subject"] = "[bckpr] backup error on " + platform.node()
    msg["From"] = FromMail
    msg["To"] = ", ".join(ToMail)

    smtp = smtplib.SMTP(SmtpServer)
    smtp.sendmail(FromMail, ToMail, msg.as_string())
    smtp.quit()


def do(fn, description):
    try:
        fn()
    except Exception as e:
        raise Exception("Error occurs while " + description, e), None, sys.exc_info()[2]


def run_backup():
    try:
        do(lambda: check_pathes_exists(), "checking pathes exists")
        do(lambda: daily_backup(), "create daily backup")
        do(lambda: weekly_backup(), "create weekly backup")
        do(lambda: monthly_backup(), "create monthly backup")
        return True
    except:
        report_error(sys.exc_info()[0])
        return False

if __name__ == "__main__":
    if run_backup():
        sys.exit(0)
    sys.exit(1)
