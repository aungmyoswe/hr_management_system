{
    "name" : "ZK Fingerprint Device Integration",
    "version" : "1.0",
    'author': 'Infinite Business Solution Co.,Ltd',
    'website': 'www.ibizmyanmar.com',
    "category" : "Custom",
    "description": "Connect to ZK Fingerprint and manage attendance records.",
    "depends" : ["base","hr","hr_attendance_extension"],
    "init_xml" : [],
    "data" : [
        "fingerprint_device_view.xml",
        # "report/daily_attendance_view.xml",
        "scheduler.xml",
        "wizard/schedule_wizard.xml",
    ],
    "active": False,
    "installable": True
}
