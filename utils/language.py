"""
═══════════════════════════════════════════════════════════════════════════
OMNIX VISION — Language / i18n Module
═══════════════════════════════════════════════════════════════════════════
Provides:
    • English + Arabic translations
    • RTL support for Arabic
    • t() translation function with smart fallback
    • Language selector UI
═══════════════════════════════════════════════════════════════════════════
"""

import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
# Language Configuration
# ══════════════════════════════════════════════════════════════════════════════

LANGUAGES = {
    "English": "en",
    "العربية": "ar",
}

RTL_LANGUAGES = {"ar"}


# ══════════════════════════════════════════════════════════════════════════════
# Translations
# ══════════════════════════════════════════════════════════════════════════════

TRANSLATIONS = {
    "en": {
        # ── Branding ──
        "app_name":       "OMNIX VISION",
        "neon_ui":        "Neon Cyber UI",
        "ultra_platform": "Ultra Platform",
        "version":        "v2.0",
        "tagline":        "AI-Powered Smart Platform",

        # ── Common Actions ──
        "back":       "← Back",
        "refresh":    "⟳ Refresh",
        "logout":     "Logout",
        "open":       "Open",
        "save":       "Save",
        "upload":     "Upload",
        "download":   "Download",
        "process":    "Process",
        "calculate":  "Calculate",
        "result":     "Result",
        "send":       "Send",
        "clear":      "Clear",
        "reset":      "Reset",
        "confirm":    "Confirm",
        "cancel":     "Cancel",
        "close":      "Close",
        "start":      "Start",
        "stop":       "Stop",
        "submit":     "Submit",
        "delete":     "Delete",
        "edit":       "Edit",
        "view":       "View",
        "yes":        "Yes",
        "no":         "No",

        # ── Language ──
        "language":        "Language",
        "select_language": "Select Language",

        # ── Status ──
        "status":          "Status",
        "active":          "Active",
        "inactive":        "Inactive",
        "running":         "Running",
        "stopped":         "Stopped",
        "ready":           "Ready",
        "partial":         "Partial",
        "not_ready":       "Not Ready",
        "online":          "Online",
        "offline":         "Offline",
        "loading":         "Loading...",
        "error":           "Error",
        "success":         "Success",
        "warning":         "Warning",
        "excellent":       "Excellent",
        "good":            "Good",
        "needs_attention": "Needs Attention",

        # ── Home ──
        "home_title":      "OMNIX VISION",
        "home_subtitle":   "Smart AI Platform for tools, media, games, and system control.",
        "welcome":         "Welcome",
        "welcome_back":    "Welcome back",
        "select_module":   "Select a module to continue using the system.",
        "core_tools":      "Core Tools",
        "interactive":     "Interactive",
        "data_info":       "Data & Info",
        "system":          "System",

        # ── Modules: Dashboard ──
        "dashboard":       "Dashboard",
        "dashboard_desc":  "View system status, results, and stored data.",
        "open_dashboard":  "Open Dashboard",

        # ── Modules: Media ──
        "media_library":      "Multimedia Center",
        "media_library_desc": "Manage your stored images, audio, and video files.",
        "open_media_library": "Open Multimedia Center",

        "media_studio":      "OMNIX MEDIA STUDIO",
        "media_desc":        "Convert and process images, audio, and video files.",
        "open_media_studio": "Open Media Studio",

        # ── Modules: Calculator ──
        "calculator":      "Calculator",
        "calculator_desc": "Perform arithmetic, scientific, and number-system operations.",
        "open_calculator": "Open Calculator",

        # ── Modules: Game ──
        "game":       "Game Center",
        "game_desc":  "Play built-in Python games with neon style.",
        "open_game":  "Open Game",

        # ── Modules: Tasks ──
        "tasks":       "Tasks",
        "tasks_desc":  "Notes, timer, and stopwatch tools.",
        "open_tasks":  "Open Tasks",

        # ── Modules: Assistant ──
        "assistant":       "Assistant",
        "assistant_desc":  "Smart AI assistant connected to the system.",
        "open_assistant":  "Open Assistant",

        # ── Modules: Camera ──
        "camera_ai":    "Camera AI",
        "camera_desc":  "Live camera processing and intelligent tracking.",
        "open_camera":  "Open Camera",

        # ── Modules: About ──
        "about_us":    "About Us",
        "about_desc":  "Learn more about the project and its purpose.",
        "open_about":  "Open About Us",

        # ── Modules: Settings ──
        "settings":       "Settings",
        "settings_desc":  "Configure your account and app preferences.",
        "open_settings":  "Open Settings",

        # ── Modules: Security Center (NEW) ──
        "security_center":      "Security Center",
        "security_center_desc": "Manage password, sessions, and account security.",
        "open_security_center": "Open Security Center",

        # ── Modules: Activity Log (NEW) ──
        "activity_log":      "Activity Log",
        "activity_log_desc": "View all your actions and login history.",
        "open_activity_log": "Open Activity Log",

        # ── Saved Data (legacy) ──
        "saved_data":       "Saved Data",
        "saved_data_desc":  "View stored information and generated system states.",
        "open_saved_data":  "Open Saved Data",

        # ── Dashboard Page ──
        "dashboard_title":    "System Dashboard",
        "dashboard_subtitle": "Monitor system state, files, tasks, camera status, and activity.",
        "system_health":      "System Health",
        "current_user":       "Current User",
        "total_files":        "Total Files",
        "storage":            "Storage",
        "file_statistics":    "File Statistics",
        "system_features":    "System Features",
        "task_summary":       "Task Summary",
        "general_summary":    "General Summary",

        # ── File Types ──
        "images":     "Images",
        "audio":      "Audio",
        "video":      "Video",
        "uploads":    "Uploads",
        "total_size": "Total Size",
        "last_file":  "Last File",

        # ── Camera / AI Vision ──
        "ai_vision":        "AI Vision Detection Center",
        "ai_vision_desc":   "Real-time camera, pose, and hand-scan monitoring system.",
        "camera":           "Camera",
        "person_detected":  "Person Detected",
        "pose_visible":     "Pose Visible",
        "right_hand":       "Right Hand",
        "left_hand":        "Left Hand",
        "body_centered":    "Body Centered",
        "system_message":   "Current System Message",
        "last_snapshot":    "Last Snapshot",
        "snapshot_count":   "Snapshot Count",
        "detection_mode":   "Detection Mode",
        "live_feedback":    "Live Feedback",

        # ── Login ──
        "login_title":    "Login",
        "username":       "Username",
        "user_id":        "User ID",
        "password":       "Password",
        "new_password":   "New Password",
        "confirm_password": "Confirm Password",
        "old_password":   "Current Password",
        "login":          "Login",
        "register":       "Register",
        "create_account": "Create Account",
        "have_account":   "Already have an account?",
        "no_account":     "Don't have an account?",
        "login_success":  "Login successful — welcome back!",
        "login_failed":   "Invalid username or password",
        "logout_success": "You have been logged out.",
        "hand_scan":      "Hand Scan",
        "credentials":    "Credentials",
        "access_granted": "Access Granted",
        "access_denied":  "Access Denied",

        # ── Security Center (NEW) ──
        "security_title":       "Security Center",
        "security_subtitle":    "Manage your account credentials and active sessions.",
        "change_password":      "Change Password",
        "password_changed":     "Password updated successfully!",
        "passwords_dont_match": "Passwords do not match.",
        "password_too_short":   "Password must be at least 4 characters.",
        "account_info":         "Account Information",
        "account_created":      "Account Created",
        "last_login_label":     "Last Login",
        "session_info":         "Session Info",
        "active_session":       "Active Session",
        "delete_account":       "Delete Account",
        "delete_warning":       "⚠️ This action is permanent. All your data will be lost.",
        "confirm_delete":       "Type your password to confirm deletion",
        "account_deleted":      "Account deleted successfully.",
        "never":                "Never",

        # ── Activity Log (NEW) ──
        "activity_title":     "Activity Log",
        "activity_subtitle":  "Full history of your actions on OMNIX VISION.",
        "no_activity":        "No activity recorded yet.",
        "clear_log":          "Clear Log",
        "log_cleared":        "Activity log cleared.",
        "filter_category":    "Filter by Category",
        "filter_all":         "All",
        "auth_category":      "Authentication",
        "navigation_category":"Navigation",
        "data_category":      "Data",
        "security_category":  "Security",
        "system_category":    "System",
        "total_actions":      "Total Actions",
        "unique_users":       "Unique Users",
        "last_action":        "Last Action",

        # ── Media Studio ──
        "image_converter": "Image Converter",
        "image_processor": "Image Processor",
        "audio_studio":    "Audio Studio",
        "video_studio":    "Video Studio",
        "history":         "History",

        # ── Calculator ──
        "basic_calculator": "Basic Calculator",
        "scientific_mode":  "Scientific Mode",
        "number_systems":   "Number Systems",
        "smart_converter":  "Smart Converter",

        # ── Games ──
        "snake_game":  "Snake Game",
        "space_game":  "Space Shooter",
        "start_game":  "Start Game",
        "high_score":  "High Score",
        "game_over":   "Game Over",
        "score":       "Score",
        "level":       "Level",

        # ── Assistant ──
        "ask_assistant":    "Ask the assistant something...",
        "quick_actions":    "Quick Actions",
        "system_status":    "System Status",
        "camera_info":      "Camera Info",
        "project_info":     "Project Info",
        "multimedia":       "Multimedia",
        "clear_chat":       "Clear Chat",
        "chat_cleared":     "Chat cleared. How can I help you?",

        # ── About ──
        "about_title":   "About OMNIX VISION",
        "about_content": "OMNIX VISION is an intelligent multimedia platform powered by AI and computer vision.",
        "team":          "Team",
        "project":       "Project",
        "technology":    "Technology",
        # ── Tasks Phase 3 ──
        "tasks_title":      "Tasks Manager",
        "tasks_subtitle":   "Organize your tasks with priorities, due dates, and tags.",
        "add_task":         "Add Task",
        "task_text":        "Task description",
        "task_placeholder": "What needs to be done?",
        "priority":         "Priority",
        "priority_low":     "Low",
        "priority_medium":  "Medium",
        "priority_high":    "High",
        "priority_urgent":  "Urgent",
        "due_date":         "Due Date",
        "no_due_date":      "No due date",
        "tag":              "Tag",
        "tags":             "Tags",
        "select_tag":       "Select a tag",
        "tag_work":         "Work",
        "tag_personal":     "Personal",
        "tag_study":        "Study",
        "tag_health":       "Health",
        "tag_shopping":     "Shopping",
        "tag_other":        "Other",
        "no_tasks":         "No tasks yet. Add one to get started!",
        "completed":        "Completed",
        "pending":          "Pending",
        "overdue":          "Overdue",
        "due_today":        "Due Today",
        "due_soon":         "Due Soon",
        "filter_status":    "Filter by status",
        "filter_priority":  "Filter by priority",
        "filter_tag":       "Filter by tag",
        "all_tasks":        "All Tasks",
        "search":           "Search",
        "search_tasks":     "Search tasks...",
        "clear_completed":  "Clear Completed",
        "clear_all":        "Clear All",
        "tasks_count":      "tasks",
        "pomodoro":         "Pomodoro Timer",
        "pomodoro_work":    "Work Session",
        "pomodoro_break":   "Break",
        "pomodoro_long_break": "Long Break",
        "minutes":          "minutes",
        "seconds":          "seconds",
        "stopwatch":        "Stopwatch",
        "start_timer":      "Start",
        "pause_timer":      "Pause",
        "resume_timer":     "Resume",
        "reset_timer":      "Reset",
        "session_complete": "Session Complete!",
        "sessions_done":    "Sessions Done",
        "files_library":    "Files Library",
        "upload_files":     "Upload Files",
        "summary":          "Summary",
        # ── Game Phase 3 ──
        "game_title":       "OMNIX Game Zone",
        "game_subtitle":    "Select a game, play, and break your record!",
        "games_available":  "Games Available",
        "total_high_score": "Total High Score",
        "best":             "Best",
        "play":             "Play",
        "now_playing":      "Now Playing",
        "choose_game":      "Choose a Game",
        # ── Assistant Phase 3 ──
        "assistant_title":  "OMNIX AI Assistant",
        "live_status":      "Live Status",
        "help":             "Help",
        # ── Tasks Extra ──
        "task_added":        "Task added successfully!",
        "task_deleted":      "Task deleted.",
        "task_completed":    "Task marked as completed!",
        "task_uncompleted":  "Task marked as pending.",
        "no_results":        "No tasks match your filters.",
        "total":             "Total",
        "edit_task":         "Edit Task",
        "today":             "Today",
        "tomorrow":          "Tomorrow",
        "yesterday":         "Yesterday",
        "days_left":         "days left",
        "days_overdue":      "days overdue",
        "due_in":            "Due in",
        "work_duration":     "Work Duration",
        "break_duration":    "Break Duration",
        "long_break_duration": "Long Break Duration",
        "current_session":   "Current Session",
        # ── Round 2 navigation ──
        "notifications":    "Notifications",
        "backup_restore":   "Backup & Restore",
        "random_tools":     "Random Tools",
        "standalone_pomo":  "Pomodoro Studio",


    },

    "ar": {
        # ── Branding ──
        "app_name":       "OMNIX VISION",
        "neon_ui":        "واجهة سايبر",
        "ultra_platform": "منصة متقدمة",
        "version":        "v2.0",
        "tagline":        "منصة ذكاء اصطناعي متقدمة",

        # ── Common Actions ──
        "back":       "→ رجوع",
        "refresh":    "⟳ تحديث",
        "logout":     "تسجيل الخروج",
        "open":       "فتح",
        "save":       "حفظ",
        "upload":     "رفع",
        "download":   "تحميل",
        "process":    "معالجة",
        "calculate":  "احسب",
        "result":     "النتيجة",
        "send":       "إرسال",
        "clear":      "مسح",
        "reset":      "إعادة تعيين",
        "confirm":    "تأكيد",
        "cancel":     "إلغاء",
        "close":      "إغلاق",
        "start":      "ابدأ",
        "stop":       "إيقاف",
        "submit":     "تقديم",
        "delete":     "حذف",
        "edit":       "تعديل",
        "view":       "عرض",
        "yes":        "نعم",
        "no":         "لا",

        # ── Language ──
        "language":        "اللغة",
        "select_language": "اختر اللغة",

        # ── Status ──
        "status":          "الحالة",
        "active":          "نشط",
        "inactive":        "غير نشط",
        "running":         "تعمل",
        "stopped":         "متوقفة",
        "ready":           "جاهز",
        "partial":         "جزئي",
        "not_ready":       "غير جاهز",
        "online":          "متصل",
        "offline":         "غير متصل",
        "loading":         "جارٍ التحميل...",
        "error":           "خطأ",
        "success":         "نجاح",
        "warning":         "تحذير",
        "excellent":       "ممتاز",
        "good":            "جيد",
        "needs_attention": "يحتاج انتباه",

        # ── Home ──
        "home_title":      "OMNIX VISION",
        "home_subtitle":   "منصة ذكاء اصطناعي للأدوات والوسائط والألعاب والتحكم بالنظام.",
        "welcome":         "مرحباً",
        "welcome_back":    "مرحباً بعودتك",
        "select_module":   "اختر وحدة للمتابعة داخل النظام.",
        "core_tools":      "الأدوات الأساسية",
        "interactive":     "تفاعلي",
        "data_info":       "البيانات والمعلومات",
        "system":          "النظام",

        # ── Modules: Dashboard ──
        "dashboard":       "لوحة التحكم",
        "dashboard_desc":  "عرض حالة النظام والنتائج والبيانات المخزنة.",
        "open_dashboard":  "فتح لوحة التحكم",

        # ── Modules: Media ──
        "media_library":      "مركز الوسائط",
        "media_library_desc": "إدارة الصور والصوت والفيديو المخزنة.",
        "open_media_library": "فتح مركز الوسائط",

        "media_studio":      "OMNIX MEDIA STUDIO",
        "media_desc":        "تحويل ومعالجة الصور والصوت والفيديو.",
        "open_media_studio": "فتح Media Studio",

        # ── Modules: Calculator ──
        "calculator":      "الحاسبة",
        "calculator_desc": "تنفيذ العمليات الحسابية والعلمية وأنظمة الأعداد.",
        "open_calculator": "فتح الحاسبة",

        # ── Modules: Game ──
        "game":       "مركز الألعاب",
        "game_desc":  "تشغيل ألعاب بايثون بأسلوب نيون داخل النظام.",
        "open_game":  "فتح الألعاب",

        # ── Modules: Tasks ──
        "tasks":       "المهام",
        "tasks_desc":  "أدوات الملاحظات والمؤقت والعداد.",
        "open_tasks":  "فتح المهام",

        # ── Modules: Assistant ──
        "assistant":       "المساعد",
        "assistant_desc":  "مساعد ذكي متصل بالنظام.",
        "open_assistant":  "فتح المساعد",

        # ── Modules: Camera ──
        "camera_ai":    "كاميرا الذكاء",
        "camera_desc":  "معالجة مباشرة للكاميرا وتتبع ذكي.",
        "open_camera":  "فتح الكاميرا",

        # ── Modules: About ──
        "about_us":    "حول النظام",
        "about_desc":  "تعرف على المشروع وهدفه.",
        "open_about":  "فتح حول النظام",

        # ── Modules: Settings ──
        "settings":       "الإعدادات",
        "settings_desc":  "ضبط حسابك وتفضيلات التطبيق.",
        "open_settings":  "فتح الإعدادات",

        # ── Modules: Security Center (NEW) ──
        "security_center":      "مركز الأمان",
        "security_center_desc": "إدارة كلمة المرور والجلسات وأمان الحساب.",
        "open_security_center": "فتح مركز الأمان",

        # ── Modules: Activity Log (NEW) ──
        "activity_log":      "سجل النشاط",
        "activity_log_desc": "عرض جميع عملياتك وتاريخ تسجيل الدخول.",
        "open_activity_log": "فتح سجل النشاط",

        # ── Saved Data (legacy) ──
        "saved_data":       "البيانات المحفوظة",
        "saved_data_desc":  "عرض المعلومات المخزنة وحالات النظام.",
        "open_saved_data":  "فتح البيانات المحفوظة",

        # ── Dashboard ──
        "dashboard_title":    "لوحة تحكم النظام",
        "dashboard_subtitle": "مراقبة حالة النظام، الملفات، المهام، الكاميرا، والنشاط.",
        "system_health":      "صحة النظام",
        "current_user":       "المستخدم الحالي",
        "total_files":        "إجمالي الملفات",
        "storage":            "التخزين",
        "file_statistics":    "إحصائيات الملفات",
        "system_features":    "ميزات النظام",
        "task_summary":       "ملخص المهام",
        "general_summary":    "الملخص العام",

        # ── File Types ──
        "images":     "الصور",
        "audio":      "الصوتيات",
        "video":      "الفيديوهات",
        "uploads":    "المرفوعات",
        "total_size": "الحجم الكلي",
        "last_file":  "آخر ملف",

        # ── Camera / AI Vision ──
        "ai_vision":        "مركز الرؤية الذكية",
        "ai_vision_desc":   "نظام مراقبة مباشر للكاميرا، وضعية الجسم، وفحص اليد.",
        "camera":           "الكاميرا",
        "person_detected":  "اكتشاف الشخص",
        "pose_visible":     "ظهور وضعية الجسم",
        "right_hand":       "اليد اليمنى",
        "left_hand":        "اليد اليسرى",
        "body_centered":    "تمركز الجسم",
        "system_message":   "رسالة النظام الحالية",
        "last_snapshot":    "آخر لقطة",
        "snapshot_count":   "عدد اللقطات",
        "detection_mode":   "وضع الكشف",
        "live_feedback":    "التغذية المباشرة",

        # ── Login ──
        "login_title":      "تسجيل الدخول",
        "username":         "اسم المستخدم",
        "user_id":          "معرف المستخدم",
        "password":         "كلمة المرور",
        "new_password":     "كلمة المرور الجديدة",
        "confirm_password": "تأكيد كلمة المرور",
        "old_password":     "كلمة المرور الحالية",
        "login":            "دخول",
        "register":         "تسجيل جديد",
        "create_account":   "إنشاء حساب",
        "have_account":     "هل لديك حساب بالفعل؟",
        "no_account":       "ليس لديك حساب؟",
        "login_success":    "تم تسجيل الدخول بنجاح — مرحباً بعودتك!",
        "login_failed":     "اسم المستخدم أو كلمة المرور غير صحيحة",
        "logout_success":   "تم تسجيل الخروج.",
        "hand_scan":        "فحص اليد",
        "credentials":      "بيانات الدخول",
        "access_granted":   "تم منح الوصول",
        "access_denied":    "تم رفض الوصول",

        # ── Security Center (NEW) ──
        "security_title":       "مركز الأمان",
        "security_subtitle":    "إدارة بيانات حسابك والجلسات النشطة.",
        "change_password":      "تغيير كلمة المرور",
        "password_changed":     "تم تحديث كلمة المرور بنجاح!",
        "passwords_dont_match": "كلمتا المرور غير متطابقتين.",
        "password_too_short":   "يجب أن تكون كلمة المرور 4 أحرف على الأقل.",
        "account_info":         "معلومات الحساب",
        "account_created":      "تاريخ الإنشاء",
        "last_login_label":     "آخر تسجيل دخول",
        "session_info":         "معلومات الجلسة",
        "active_session":       "جلسة نشطة",
        "delete_account":       "حذف الحساب",
        "delete_warning":       "⚠️ هذا الإجراء دائم. ستفقد جميع بياناتك.",
        "confirm_delete":       "اكتب كلمة المرور للتأكيد",
        "account_deleted":      "تم حذف الحساب بنجاح.",
        "never":                "أبداً",

        # ── Activity Log (NEW) ──
        "activity_title":      "سجل النشاط",
        "activity_subtitle":   "تاريخ كامل لعملياتك على OMNIX VISION.",
        "no_activity":         "لا توجد عمليات مسجلة بعد.",
        "clear_log":           "مسح السجل",
        "log_cleared":         "تم مسح سجل النشاط.",
        "filter_category":     "تصفية حسب الفئة",
        "filter_all":          "الكل",
        "auth_category":       "المصادقة",
        "navigation_category": "التنقل",
        "data_category":       "البيانات",
        "security_category":   "الأمان",
        "system_category":     "النظام",
        "total_actions":       "إجمالي العمليات",
        "unique_users":        "المستخدمون الفريدون",
        "last_action":         "آخر عملية",

        # ── Media Studio ──
        "image_converter": "محول الصور",
        "image_processor": "معالج الصور",
        "audio_studio":    "استوديو الصوت",
        "video_studio":    "استوديو الفيديو",
        "history":         "السجل",

        # ── Calculator ──
        "basic_calculator": "الحاسبة الأساسية",
        "scientific_mode":  "الوضع العلمي",
        "number_systems":   "أنظمة الأعداد",
        "smart_converter":  "المحول الذكي",

        # ── Games ──
        "snake_game":  "لعبة الدودة",
        "space_game":  "لعبة الطائرة",
        "start_game":  "ابدأ اللعبة",
        "high_score":  "أعلى نقطة",
        "game_over":   "انتهت اللعبة",
        "score":       "النقاط",
        "level":       "المستوى",

        # ── Assistant ──
        "ask_assistant":    "اسأل المساعد...",
        "quick_actions":    "إجراءات سريعة",
        "system_status":    "حالة النظام",
        "camera_info":      "معلومات الكاميرا",
        "project_info":     "معلومات المشروع",
        "multimedia":       "الوسائط المتعددة",
        "clear_chat":       "مسح المحادثة",
        "chat_cleared":     "تم مسح المحادثة. كيف يمكنني مساعدتك؟",

        # ── About ──
        "about_title":   "حول OMNIX VISION",
        "about_content": "OMNIX VISION منصة وسائط ذكية مدعومة بالذكاء الاصطناعي والرؤية الحاسوبية.",
        "team":          "الفريق",
        "project":       "المشروع",
        "technology":    "التقنية",
        # ── Tasks Phase 3 ──
        "tasks_title":      "مدير المهام",
        "tasks_subtitle":   "نظم مهامك بأولويات وتواريخ استحقاق وعلامات.",
        "add_task":         "إضافة مهمة",
        "task_text":        "وصف المهمة",
        "task_placeholder": "ماذا تريد إنجازه؟",
        "priority":         "الأولوية",
        "priority_low":     "منخفضة",
        "priority_medium":  "متوسطة",
        "priority_high":    "عالية",
        "priority_urgent":  "عاجلة",
        "due_date":         "تاريخ الاستحقاق",
        "no_due_date":      "بدون تاريخ",
        "tag":              "علامة",
        "tags":             "العلامات",
        "select_tag":       "اختر علامة",
        "tag_work":         "عمل",
        "tag_personal":     "شخصي",
        "tag_study":        "دراسة",
        "tag_health":       "صحة",
        "tag_shopping":     "تسوق",
        "tag_other":        "أخرى",
        "no_tasks":         "لا توجد مهام بعد. أضف واحدة للبدء!",
        "completed":        "مكتملة",
        "pending":          "قيد التنفيذ",
        "overdue":          "متأخرة",
        "due_today":        "اليوم",
        "due_soon":         "قريباً",
        "filter_status":    "تصفية حسب الحالة",
        "filter_priority":  "تصفية حسب الأولوية",
        "filter_tag":       "تصفية حسب العلامة",
        "all_tasks":        "كل المهام",
        "search":           "بحث",
        "search_tasks":     "ابحث عن المهام...",
        "clear_completed":  "مسح المكتملة",
        "clear_all":        "مسح الكل",
        "tasks_count":      "مهام",
        "pomodoro":         "مؤقت بومودورو",
        "pomodoro_work":    "جلسة عمل",
        "pomodoro_break":   "استراحة",
        "pomodoro_long_break": "استراحة طويلة",
        "minutes":          "دقيقة",
        "seconds":          "ثانية",
        "stopwatch":        "ساعة إيقاف",
        "start_timer":      "ابدأ",
        "pause_timer":      "إيقاف مؤقت",
        "resume_timer":     "استئناف",
        "reset_timer":      "إعادة تعيين",
        "session_complete": "اكتملت الجلسة!",
        "sessions_done":    "الجلسات المكتملة",
        "files_library":    "مكتبة الملفات",
        "upload_files":     "رفع الملفات",
        "summary":          "ملخص",
        # ── Game Phase 3 ──
        "game_title":       "منطقة OMNIX للألعاب",
        "game_subtitle":    "اختر لعبة، العب، واكسر رقمك القياسي!",
        "games_available":  "الألعاب المتاحة",
        "total_high_score": "إجمالي أعلى النقاط",
        "best":             "أفضل",
        "play":             "العب",
        "now_playing":      "يلعب الآن",
        "choose_game":      "اختر لعبة",
        # ── Assistant Phase 3 ──
        "assistant_title":  "مساعد OMNIX الذكي",
        "live_status":      "الحالة المباشرة",
        "help":             "مساعدة",
        # ── Tasks Extra ──
        "task_added":        "تمت إضافة المهمة بنجاح!",
        "task_deleted":      "تم حذف المهمة.",
        "task_completed":    "تم وضع علامة على المهمة كمكتملة!",
        "task_uncompleted":  "تم إرجاع المهمة لقيد التنفيذ.",
        "no_results":        "لا توجد مهام تطابق التصفية.",
        "total":             "الإجمالي",
        "edit_task":         "تعديل المهمة",
        "today":             "اليوم",
        "tomorrow":          "غداً",
        "yesterday":         "أمس",
        "days_left":         "يوم متبقي",
        "days_overdue":      "يوم متأخر",
        "due_in":            "متبقي",
        "work_duration":     "مدة العمل",
        "break_duration":    "مدة الاستراحة",
        "long_break_duration": "مدة الاستراحة الطويلة",
        "current_session":   "الجلسة الحالية",
        # ── Round 2 navigation ──
        "notifications":    "الإشعارات",
        "backup_restore":   "النسخ الاحتياطي",
        "random_tools":     "أدوات عشوائية",
        "standalone_pomo":  "استوديو بومودورو",


    }
}


# ══════════════════════════════════════════════════════════════════════════════
# Core Helpers
# ══════════════════════════════════════════════════════════════════════════════

def init_language():
    """Initialize language in session state if not already set."""
    if "language" not in st.session_state:
        st.session_state.language = "English"


def get_language_code() -> str:
    """Return the current ISO language code (e.g. 'en', 'ar')."""
    init_language()
    return LANGUAGES.get(st.session_state.language, "en")


def is_rtl() -> bool:
    """Return True if the current language is right-to-left."""
    return get_language_code() in RTL_LANGUAGES


def t(key: str, fallback: str = "") -> str:
    """
    Translate a key to the current language.
    Falls back to English, then to the key itself (or fallback if provided).
    """
    lang_code = get_language_code()
    lang_dict = TRANSLATIONS.get(lang_code, TRANSLATIONS["en"])
    value = lang_dict.get(key)
    if value is not None:
        return value
    # Try English fallback
    en_value = TRANSLATIONS["en"].get(key)
    if en_value is not None:
        return en_value
    return fallback if fallback else key


def t_plural(key_singular: str, key_plural: str, count: int) -> str:
    """Return singular or plural translation based on count."""
    return t(key_singular) if count == 1 else t(key_plural)


def apply_rtl_css():
    """Inject RTL CSS when Arabic is selected."""
    if is_rtl():
        st.markdown("""
        <style>
        .stApp, .block-container, .stMarkdown, .stButton,
        div[data-testid="stVerticalBlock"], div[data-testid="column"] {
            direction: rtl !important;
            text-align: right !important;
        }
        .stTextInput input, .stSelectbox select, .stTextArea textarea {
            direction: rtl !important;
            text-align: right !important;
        }
        /* Keep Orbitron headers LTR for branding consistency */
        h1, h2, h3, .orbitron-keep-ltr {
            direction: ltr !important;
            text-align: center !important;
        }
        </style>
        """, unsafe_allow_html=True)


def render_language_selector(key: str = "global_language_selector"):
    """
    Render a selectbox for language selection.
    Triggers st.rerun() when the language changes.
    """
    init_language()

    options = list(LANGUAGES.keys())
    current_index = options.index(st.session_state.language) if st.session_state.language in options else 0

    selected = st.selectbox(
        t("select_language"),
        options,
        index=current_index,
        key=key
    )

    if selected != st.session_state.language:
        st.session_state.language = selected
        st.rerun()


def get_all_keys() -> list:
    """Return all translation keys available in English."""
    return list(TRANSLATIONS["en"].keys())


def missing_translations(lang_code: str = "ar") -> list:
    """Return keys that exist in English but are missing in the given language."""
    en_keys   = set(TRANSLATIONS["en"].keys())
    lang_keys = set(TRANSLATIONS.get(lang_code, {}).keys())
    return sorted(en_keys - lang_keys)
