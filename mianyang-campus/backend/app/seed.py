from datetime import date, timedelta
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.campus import CampusFigure, CampusScenery
from app.models.academic import Course, Grade
from app.models.growth import GrowthRecord, RecordType
from app.models.service import ServiceTicket, TicketType, TicketStatus
from app.models.leave import LeaveRequest, LeaveType, LeaveStatus
from app.models.crisis import AIDialogSummary, CrisisLevel
from app.models.knowledge import KnowledgeItem

is_fresh = False

# Rebuild tables for schema changes
for model in [GrowthRecord, Grade, Course, LeaveRequest, ServiceTicket, AIDialogSummary]:
    try:
        model.__table__.drop(engine)
        print(f"Dropped {model.__tablename__}")
    except Exception:
        pass

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ─── 用户（仅在首次时创建）──────────────────────────────────────
if db.query(User).count() == 0:
    is_fresh = True
    users = [
        User(username="2024001", password_hash=hash_password("123456"), name="张三", role=UserRole.STUDENT, college="软件学院"),
        User(username="2024002", password_hash=hash_password("123456"), name="李四", role=UserRole.STUDENT, college="软件学院"),
        User(username="2024003", password_hash=hash_password("123456"), name="王五", role=UserRole.STUDENT, college="大数据学院"),
        User(username="t1001", password_hash=hash_password("123456"), name="王老师", role=UserRole.TEACHER, college="软件学院"),
        User(username="t1002", password_hash=hash_password("123456"), name="李老师", role=UserRole.TEACHER, college="大数据学院"),
        User(username="admin", password_hash=hash_password("admin123"), name="管理员", role=UserRole.ADMIN),
        # 辅导员
        User(username="t1003", password_hash=hash_password("123456"), name="陈慧敏", role=UserRole.TEACHER, college="软件学院"),
        User(username="t1004", password_hash=hash_password("123456"), name="张伟明", role=UserRole.TEACHER, college="大数据学院"),
        User(username="t1005", password_hash=hash_password("123456"), name="刘雅婷", role=UserRole.TEACHER, college="建筑工程学院"),
        User(username="t1006", password_hash=hash_password("123456"), name="赵志强", role=UserRole.TEACHER, college="经济管理学院"),
        User(username="t1007", password_hash=hash_password("123456"), name="林晓娟", role=UserRole.TEACHER, college="现代服务学院"),
    ]
    db.add_all(users)
    db.commit()

# ─── 补充学生（无则追加）────────────────────────────────────────
new_students = [
    ("2024003", "王五", "大数据学院"),
    ("2024004", "赵六", "软件学院"),
    ("2024005", "钱七", "大数据学院"),
    ("2024006", "孙八", "建筑工程学院"),
    ("2024007", "周九", "经济管理学院"),
    ("2024008", "吴十", "现代服务学院"),
    ("2024009", "郑十一", "软件学院"),
]
for su, sn, sc in new_students:
    if not db.query(User).filter(User.username == su).first():
        db.add(User(username=su, password_hash=hash_password("123456"), name=sn, role=UserRole.STUDENT, college=sc))
db.commit()

# ─── 设置学生-导师绑定 ──────────────────────────────────────────
# 陈慧敏(t1003): 张三 + 赵六 + 郑十一（同导师多人，测试聚合）
# 张伟明(t1004): 王五 + 钱七（同导师，测试同步）
# 刘雅婷(t1005): 孙八
# 赵志强(t1006): 周九
# 林晓娟(t1007): 吴十
# 李四(2024002): 无导师（测试未分配场景）
tutor_bindings = [
    ("2024001", "t1003"),  # 张三 → 陈慧敏
    ("2024003", "t1004"),  # 王五 → 张伟明
    ("2024004", "t1003"),  # 赵六 → 陈慧敏（同导师）
    ("2024005", "t1004"),  # 钱七 → 张伟明（同导师）
    ("2024006", "t1005"),  # 孙八 → 刘雅婷
    ("2024007", "t1006"),  # 周九 → 赵志强
    ("2024008", "t1007"),  # 吴十 → 林晓娟
    ("2024009", "t1003"),  # 郑十一 → 陈慧敏（同导师）
]
for su, tu in tutor_bindings:
    s = db.query(User).filter(User.username == su).first()
    t = db.query(User).filter(User.username == tu).first()
    if s and t and not s.tutor_id:
        s.tutor_id = t.id
db.commit()


# ─── 辅助：通过学号查找学生ID ──────────────────────────────────
def sid(username: str) -> int:
    u = db.query(User).filter(User.username == username).first()
    return u.id if u else 0


# ─── 校园人物 & 风景 ────────────────────────────────────────────
if db.query(CampusFigure).count() == 0:
    db.add_all([
        CampusFigure(name="张三", title="国家奖学金获得者", avatar="/images/avatar1.jpg", description="软件学院2022级学生，GPA 3.5+", category="student"),
        CampusFigure(name="赵六", title="ACM竞赛金牌得主", avatar="/images/avatar2.jpg", description="ICPC亚洲区域赛金牌，软件学院", category="student"),
        CampusFigure(name="周九", title="优秀学生干部", avatar="/images/avatar3.jpg", description="经济管理学院学生会主席", category="student"),
        CampusFigure(name="王老师", title="优秀教师", avatar="/images/avatar4.jpg", description="软件学院副教授，主持多项省级课题", category="teacher"),
        CampusFigure(name="陈慧敏", title="优秀辅导员", avatar="/images/avatar5.jpg", description="软件学院辅导员，从事学生工作10年", category="teacher"),
    ])
    db.commit()

if db.query(CampusScenery).count() == 0:
    db.add_all([
        CampusScenery(title="图书馆（安州）", image_url="/images/lib_anzhou.jpg", description="现代化学习空间", location="校园中心", area="anzhou"),
        CampusScenery(title="教学楼群（安州）", image_url="/images/teaching_anzhou.jpg", description="安州主教学区", location="校园东侧", area="anzhou"),
        CampusScenery(title="校园湖景（安州）", image_url="/images/lake_anzhou.jpg", description="安州休闲景区", location="校园西侧", area="anzhou"),
        CampusScenery(title="图书馆（游仙）", image_url="/images/lib_youxian.jpg", description="游仙图书馆", location="校园中心", area="youxian"),
        CampusScenery(title="教学楼群（游仙）", image_url="/images/teaching_youxian.jpg", description="游仙主教学区", location="校园东侧", area="youxian"),
        CampusScenery(title="校园林荫道（游仙）", image_url="/images/tree_youxian.jpg", description="游仙林荫大道", location="主干道", area="youxian"),
    ])
    db.commit()

# ─── 知识库 ─────────────────────────────────────────────────────
if db.query(KnowledgeItem).count() == 0:
    db.add_all([
        KnowledgeItem(category="办事流程", question="怎么请假", answer="请假流程：学生可在对话框输入请假需求，我会自动生成请假申请。也可通过办事服务页面手动提交。"),
        KnowledgeItem(category="办事流程", question="如何申请在校证明", answer="1. 登录系统 2. 进入办事服务页面 3. 选择证明申请 4. 填写信息 5. 审批通过后可在电子版下载。"),
        KnowledgeItem(category="办事流程", question="怎么查课表", answer="对话框输入'查课表'或'今天有什么课'，我会自动调取课表信息。"),
        KnowledgeItem(category="办事流程", question="怎么查成绩", answer="对话框输入'查成绩'自动调取成绩信息，也可到成绩查询页面查看。"),
        KnowledgeItem(category="校园导航", question="图书馆在哪里", answer="安州校区位于校园中心；游仙校区位于校园中心区域。"),
        KnowledgeItem(category="校园导航", question="食堂营业时间", answer="早餐7:00-9:00，午餐11:30-13:00，晚餐17:30-19:00。"),
        KnowledgeItem(category="校园导航", question="体育馆开放时间", answer="周一至周五6:30-21:30，周末8:00-21:00。"),
        KnowledgeItem(category="规章制度", question="宿舍管理规定", answer="按时归寝(23:00前)，禁止违规电器，保持卫生，不得留宿外人。"),
        KnowledgeItem(category="规章制度", question="考试纪律", answer="提前15分钟入场，携带学生证，禁止手机，严禁作弊。"),
        KnowledgeItem(category="规章制度", question="奖学金评定标准", answer="学年GPA排名、综合素质测评、无违纪处分。"),
        KnowledgeItem(category="校园生活", question="校园卡怎么充值", answer="微信小程序、食堂充值窗口、自助充值机。"),
        KnowledgeItem(category="校园生活", question="心理咨询中心", answer="行政楼3楼305室，紧急情况可联系辅导员。"),
    ])
    db.commit()

# ─── 课表（每个学生专属课程，测试独立性）───────────────────────
if db.query(Course).count() == 0:
    all_courses = []
    # 张三 (2024001)
    all_courses += [
        Course(student_id=sid("2024001"), name="软件工程", teacher="王老师", location="教学楼301", day_of_week=1, start_period=1, end_period=2, week_start=1, week_end=16),
        Course(student_id=sid("2024001"), name="数据结构", teacher="赵老师", location="教学楼205", day_of_week=1, start_period=3, end_period=4, week_start=1, week_end=16),
        Course(student_id=sid("2024001"), name="操作系统", teacher="陈老师", location="教学楼302", day_of_week=3, start_period=1, end_period=2, week_start=1, week_end=16),
        Course(student_id=sid("2024001"), name="计算机网络", teacher="刘老师", location="实验楼401", day_of_week=5, start_period=5, end_period=6, week_start=1, week_end=16),
    ]
    # 李四 (2024002)
    all_courses += [
        Course(student_id=sid("2024002"), name="软件工程", teacher="王老师", location="教学楼301", day_of_week=1, start_period=3, end_period=4, week_start=1, week_end=16),
        Course(student_id=sid("2024002"), name="数据库原理", teacher="李老师", location="教学楼203", day_of_week=2, start_period=1, end_period=2, week_start=1, week_end=16),
        Course(student_id=sid("2024002"), name="Web前端开发", teacher="张老师", location="实验楼301", day_of_week=4, start_period=5, end_period=6, week_start=1, week_end=16),
    ]
    # 王五 (2024003)
    all_courses += [
        Course(student_id=sid("2024003"), name="大数据导论", teacher="李老师", location="教学楼402", day_of_week=2, start_period=3, end_period=4, week_start=1, week_end=16),
        Course(student_id=sid("2024003"), name="Python数据分析", teacher="周老师", location="实验楼502", day_of_week=3, start_period=5, end_period=6, week_start=1, week_end=16),
        Course(student_id=sid("2024003"), name="机器学习基础", teacher="吴老师", location="教学楼401", day_of_week=5, start_period=1, end_period=2, week_start=1, week_end=16),
    ]
    # 赵六 (2024004)
    all_courses += [
        Course(student_id=sid("2024004"), name="算法设计与分析", teacher="陈老师", location="教学楼301", day_of_week=2, start_period=5, end_period=6, week_start=1, week_end=16),
        Course(student_id=sid("2024004"), name="C++程序设计", teacher="赵老师", location="实验楼401", day_of_week=3, start_period=1, end_period=2, week_start=1, week_end=16),
        Course(student_id=sid("2024004"), name="离散数学", teacher="王老师", location="教学楼302", day_of_week=4, start_period=3, end_period=4, week_start=1, week_end=16),
    ]
    # 钱七 (2024005)
    all_courses += [
        Course(student_id=sid("2024005"), name="大数据导论", teacher="李老师", location="教学楼402", day_of_week=1, start_period=5, end_period=6, week_start=1, week_end=16),
        Course(student_id=sid("2024005"), name="统计学", teacher="刘老师", location="教学楼303", day_of_week=3, start_period=3, end_period=4, week_start=1, week_end=16),
    ]
    # 孙八 (2024006)
    all_courses += [
        Course(student_id=sid("2024006"), name="建筑材料", teacher="黄老师", location="建工楼101", day_of_week=1, start_period=1, end_period=2, week_start=1, week_end=16),
        Course(student_id=sid("2024006"), name="建筑制图", teacher="杨老师", location="建工楼204", day_of_week=3, start_period=5, end_period=6, week_start=1, week_end=16),
    ]
    # 周九 (2024007)
    all_courses += [
        Course(student_id=sid("2024007"), name="微观经济学", teacher="赵老师", location="经管楼301", day_of_week=2, start_period=1, end_period=2, week_start=1, week_end=16),
        Course(student_id=sid("2024007"), name="管理学原理", teacher="孙老师", location="经管楼302", day_of_week=4, start_period=3, end_period=4, week_start=1, week_end=16),
        Course(student_id=sid("2024007"), name="会计学基础", teacher="钱老师", location="经管楼303", day_of_week=5, start_period=5, end_period=6, week_start=1, week_end=16),
    ]
    # 吴十 (2024008)
    all_courses += [
        Course(student_id=sid("2024008"), name="现代服务管理", teacher="林老师", location="服务楼201", day_of_week=1, start_period=5, end_period=6, week_start=1, week_end=16),
        Course(student_id=sid("2024008"), name="客户关系管理", teacher="陈老师", location="服务楼202", day_of_week=3, start_period=1, end_period=2, week_start=1, week_end=16),
    ]
    # 郑十一 (2024009)
    all_courses += [
        Course(student_id=sid("2024009"), name="软件工程", teacher="王老师", location="教学楼301", day_of_week=1, start_period=5, end_period=6, week_start=1, week_end=16),
        Course(student_id=sid("2024009"), name="Java程序设计", teacher="张老师", location="实验楼301", day_of_week=4, start_period=1, end_period=2, week_start=1, week_end=16),
    ]
    db.add_all(all_courses)
    db.commit()

# ─── 成绩（每个学生不同成绩分布）─────────────────────────────────
if db.query(Grade).count() == 0:
    all_grades = []
    # 张三 — 稳步上升，中上水平
    zs = sid("2024001")
    all_grades += [
        Grade(student_id=zs, course_name="高等数学(上)", score=72, credit=4, gpa=2.8, semester="2023-2024-1"),
        Grade(student_id=zs, course_name="大学英语(1)", score=68, credit=3, gpa=2.5, semester="2023-2024-1"),
        Grade(student_id=zs, course_name="思修", score=85, credit=2, gpa=3.5, semester="2023-2024-1"),
        Grade(student_id=zs, course_name="高等数学(下)", score=78, credit=4, gpa=3.0, semester="2023-2024-2"),
        Grade(student_id=zs, course_name="大学英语(2)", score=75, credit=3, gpa=2.8, semester="2023-2024-2"),
        Grade(student_id=zs, course_name="C语言", score=82, credit=3, gpa=3.3, semester="2023-2024-2"),
        Grade(student_id=zs, course_name="线性代数", score=80, credit=3, gpa=3.2, semester="2023-2024-2"),
        Grade(student_id=zs, course_name="高等数学(上)", score=85, credit=4, gpa=3.5, semester="2024-2025-1"),
        Grade(student_id=zs, course_name="大学英语", score=78, credit=3, gpa=3.0, semester="2024-2025-1"),
        Grade(student_id=zs, course_name="程序设计基础", score=92, credit=3, gpa=4.0, semester="2024-2025-1"),
        Grade(student_id=zs, course_name="概率论", score=88, credit=3, gpa=3.7, semester="2024-2025-2"),
        Grade(student_id=zs, course_name="数据结构", score=86, credit=4, gpa=3.6, semester="2024-2025-2"),
        Grade(student_id=zs, course_name="数据库原理", score=90, credit=3, gpa=3.8, semester="2024-2025-2"),
        Grade(student_id=zs, course_name="Python", score=93, credit=2, gpa=4.0, semester="2024-2025-2"),
    ]
    # 李四 — 成绩波动大，有挂科风险
    ls = sid("2024002")
    all_grades += [
        Grade(student_id=ls, course_name="高等数学(上)", score=61, credit=4, gpa=2.0, semester="2023-2024-1"),
        Grade(student_id=ls, course_name="大学英语(1)", score=55, credit=3, gpa=1.5, semester="2023-2024-1"),
        Grade(student_id=ls, course_name="思修", score=70, credit=2, gpa=2.5, semester="2023-2024-1"),
        Grade(student_id=ls, course_name="高等数学(下)", score=52, credit=4, gpa=1.3, semester="2023-2024-2"),
        Grade(student_id=ls, course_name="大学英语(2)", score=65, credit=3, gpa=2.2, semester="2023-2024-2"),
        Grade(student_id=ls, course_name="C语言", score=45, credit=3, gpa=0.0, semester="2023-2024-2"),
        Grade(student_id=ls, course_name="软件工程", score=72, credit=3, gpa=2.8, semester="2024-2025-1"),
        Grade(student_id=ls, course_name="数据库原理", score=68, credit=3, gpa=2.5, semester="2024-2025-1"),
        Grade(student_id=ls, course_name="Web前端开发", score=80, credit=3, gpa=3.2, semester="2024-2025-2"),
    ]
    # 王五 — 学霸型，高GPA
    ww = sid("2024003")
    all_grades += [
        Grade(student_id=ww, course_name="高等数学(上)", score=91, credit=4, gpa=4.0, semester="2023-2024-1"),
        Grade(student_id=ww, course_name="大学英语(1)", score=88, credit=3, gpa=3.7, semester="2023-2024-1"),
        Grade(student_id=ww, course_name="思修", score=90, credit=2, gpa=3.9, semester="2023-2024-1"),
        Grade(student_id=ww, course_name="高等数学(下)", score=93, credit=4, gpa=4.0, semester="2023-2024-2"),
        Grade(student_id=ww, course_name="大学英语(2)", score=85, credit=3, gpa=3.5, semester="2023-2024-2"),
        Grade(student_id=ww, course_name="C语言", score=92, credit=3, gpa=4.0, semester="2023-2024-2"),
        Grade(student_id=ww, course_name="线性代数", score=90, credit=3, gpa=3.9, semester="2023-2024-2"),
        Grade(student_id=ww, course_name="大数据导论", score=94, credit=3, gpa=4.0, semester="2024-2025-1"),
        Grade(student_id=ww, course_name="Python数据分析", score=96, credit=3, gpa=4.0, semester="2024-2025-1"),
        Grade(student_id=ww, course_name="机器学习基础", score=91, credit=3, gpa=4.0, semester="2024-2025-2"),
        Grade(student_id=ww, course_name="统计学", score=89, credit=3, gpa=3.8, semester="2024-2025-2"),
    ]
    # 赵六 — 竞赛型，成绩中上
    zl = sid("2024004")
    all_grades += [
        Grade(student_id=zl, course_name="高等数学(上)", score=78, credit=4, gpa=3.0, semester="2023-2024-1"),
        Grade(student_id=zl, course_name="离散数学", score=85, credit=3, gpa=3.5, semester="2023-2024-1"),
        Grade(student_id=zl, course_name="C++程序设计", score=82, credit=4, gpa=3.3, semester="2023-2024-1"),
        Grade(student_id=zl, course_name="算法设计", score=88, credit=3, gpa=3.7, semester="2024-2025-1"),
        Grade(student_id=zl, course_name="数据结构", score=90, credit=4, gpa=3.9, semester="2024-2025-1"),
    ]
    # 钱七 — 成绩下滑，情绪问题
    qq = sid("2024005")
    all_grades += [
        Grade(student_id=qq, course_name="高等数学(上)", score=75, credit=4, gpa=2.8, semester="2023-2024-1"),
        Grade(student_id=qq, course_name="大学英语(1)", score=70, credit=3, gpa=2.5, semester="2023-2024-1"),
        Grade(student_id=qq, course_name="大数据导论", score=65, credit=3, gpa=2.2, semester="2024-2025-1"),
        Grade(student_id=qq, course_name="统计学", score=58, credit=3, gpa=1.5, semester="2024-2025-1"),
    ]
    # 周九 — 优异生，GPA 3.8+
    zj = sid("2024007")
    all_grades += [
        Grade(student_id=zj, course_name="微观经济学", score=92, credit=3, gpa=4.0, semester="2023-2024-1"),
        Grade(student_id=zj, course_name="管理学原理", score=95, credit=3, gpa=4.0, semester="2023-2024-1"),
        Grade(student_id=zj, course_name="会计学基础", score=88, credit=3, gpa=3.7, semester="2023-2024-1"),
        Grade(student_id=zj, course_name="宏观经济学", score=90, credit=3, gpa=3.9, semester="2024-2025-1"),
        Grade(student_id=zj, course_name="财务管理", score=93, credit=3, gpa=4.0, semester="2024-2025-1"),
    ]
    # 吴十 — 请假频繁，成绩一般
    ws = sid("2024008")
    all_grades += [
        Grade(student_id=ws, course_name="现代服务管理", score=72, credit=3, gpa=2.8, semester="2023-2024-1"),
        Grade(student_id=ws, course_name="客户关系管理", score=68, credit=3, gpa=2.5, semester="2023-2024-1"),
        Grade(student_id=ws, course_name="职场礼仪", score=80, credit=2, gpa=3.2, semester="2024-2025-1"),
    ]
    db.add_all(all_grades)
    db.commit()

# ─── 成长记录（体现学生个性差异）─────────────────────────────────
if db.query(GrowthRecord).count() == 0:
    now = date.today()
    records = []

    # 张三 — 全面型：竞赛+荣誉+实践
    zs = sid("2024001")
    records += [
        GrowthRecord(student_id=zs, type=RecordType.COMPETITION, title="ACM校赛一等奖", date=now - timedelta(days=180), organizer="软件学院", competition_level="校级"),
        GrowthRecord(student_id=zs, type=RecordType.HONOR, title="国家励志奖学金", date=now - timedelta(days=60), honor_level="国家级"),
        GrowthRecord(student_id=zs, type=RecordType.PRACTICE, title="暑期企业实训", date=now - timedelta(days=120), practice_type="企业实习", practice_certificate="优秀实习生"),
        GrowthRecord(student_id=zs, type=RecordType.ACHIEVEMENT, title="基于AI的考勤系统", date=now - timedelta(days=30), achievement_type="软件著作权"),
    ]

    # 李四 — 活跃型：实践为主，少量竞赛
    ls = sid("2024002")
    records += [
        GrowthRecord(student_id=ls, type=RecordType.PRACTICE, title="社区志愿服务", date=now - timedelta(days=200), practice_type="志愿服务"),
        GrowthRecord(student_id=ls, type=RecordType.PRACTICE, title="迎新志愿者", date=now - timedelta(days=90), practice_type="志愿服务"),
        GrowthRecord(student_id=ls, type=RecordType.COMPETITION, title="程序设计天梯赛", date=now - timedelta(days=150), organizer="计算机学院", competition_level="省级"),
    ]

    # 王五 — 学术型：论文+成果+竞赛
    ww = sid("2024003")
    records += [
        GrowthRecord(student_id=ww, type=RecordType.PAPER, title="基于大数据的用户画像研究", date=now - timedelta(days=45), paper_type="期刊论文", paper_name="计算机应用研究", first_author="王五"),
        GrowthRecord(student_id=ww, type=RecordType.COMPETITION, title="数学建模国赛省一等奖", date=now - timedelta(days=200), organizer="中国工业与应用数学学会", competition_level="省级"),
        GrowthRecord(student_id=ww, type=RecordType.ACHIEVEMENT, title="数据可视化平台", date=now - timedelta(days=100), achievement_type="软件著作权"),
        GrowthRecord(student_id=ww, type=RecordType.HONOR, title="优秀学生标兵", date=now - timedelta(days=30), honor_level="校级"),
    ]

    # 赵六 — 竞赛狂魔
    zl = sid("2024004")
    records += [
        GrowthRecord(student_id=zl, type=RecordType.COMPETITION, title="ICPC亚洲区域赛银奖", date=now - timedelta(days=250), organizer="ACM/ICPC", competition_level="亚洲区"),
        GrowthRecord(student_id=zl, type=RecordType.COMPETITION, title="蓝桥杯省一等奖", date=now - timedelta(days=150), organizer="工业和信息化部", competition_level="省级"),
        GrowthRecord(student_id=zl, type=RecordType.HONOR, title="创新能力先进个人", date=now - timedelta(days=60), honor_level="校级"),
    ]

    # 钱七 — 少量荣誉（危机案例）
    qq = sid("2024005")
    records += [
        GrowthRecord(student_id=qq, type=RecordType.HONOR, title="优秀志愿者", date=now - timedelta(days=300), honor_level="院级"),
    ]

    # 孙八 — 刚入学，少量
    sb = sid("2024006")
    records += [
        GrowthRecord(student_id=sb, type=RecordType.PRACTICE, title="新生军训优秀学员", date=now - timedelta(days=30), practice_type="军训"),
    ]

    # 周九 — 荣誉收割机
    zj = sid("2024007")
    records += [
        GrowthRecord(student_id=zj, type=RecordType.HONOR, title="国家奖学金", date=now - timedelta(days=90), honor_level="国家级"),
        GrowthRecord(student_id=zj, type=RecordType.HONOR, title="优秀学生干部", date=now - timedelta(days=180), honor_level="校级"),
        GrowthRecord(student_id=zj, type=RecordType.PAPER, title="共享经济下的大学生消费行为", date=now - timedelta(days=60), paper_type="普刊论文", paper_name="经济研究导刊", first_author="周九"),
        GrowthRecord(student_id=zj, type=RecordType.COMPETITION, title="全国大学生市场调查大赛省一等奖", date=now - timedelta(days=120), organizer="教育部统计学教指委", competition_level="省级"),
        GrowthRecord(student_id=zj, type=RecordType.PRACTICE, title="农业银行实习", date=now - timedelta(days=200), practice_type="企业实习", practice_certificate="优秀实习生"),
    ]

    # 吴十 — 缺席多，无成长记录
    # 吴十故意没有成长记录，测试空状态

    db.add_all(records)
    db.commit()

# ─── 请假记录（测试审批流）──────────────────────────────────────
if db.query(LeaveRequest).count() == 0:
    now = date.today()
    leaves = []

    # 张三 — 有已通过和待审批
    zs = sid("2024001")
    leaves += [
        LeaveRequest(student_id=zs, start_date=now - timedelta(days=60), end_date=now - timedelta(days=58), reason="参加ACM校赛", leave_type=LeaveType.COMPETITION, status=LeaveStatus.APPROVED),
        LeaveRequest(student_id=zs, start_date=now + timedelta(days=5), end_date=now + timedelta(days=7), reason="下周二参加ACM区域赛需要请假三天", leave_type=LeaveType.COMPETITION, status=LeaveStatus.PENDING),
    ]

    # 李四 — 有被拒和待审批
    ls = sid("2024002")
    leaves += [
        LeaveRequest(student_id=ls, start_date=now - timedelta(days=30), end_date=now - timedelta(days=28), reason="回家办事", leave_type=LeaveType.PERSONAL, status=LeaveStatus.REJECTED, reject_reason="理由不充分，请补充详细信息"),
        LeaveRequest(student_id=ls, start_date=now + timedelta(days=3), end_date=now + timedelta(days=3), reason="身体不舒服想去医院检查", leave_type=LeaveType.SICK, status=LeaveStatus.PENDING),
    ]

    # 吴十 — 频繁请假（测试请假型学生）
    ws = sid("2024008")
    leaves += [
        LeaveRequest(student_id=ws, start_date=now - timedelta(days=90), end_date=now - timedelta(days=90), reason="家中有事", leave_type=LeaveType.PERSONAL, status=LeaveStatus.APPROVED),
        LeaveRequest(student_id=ws, start_date=now - timedelta(days=45), end_date=now - timedelta(days=45), reason="身体不适", leave_type=LeaveType.SICK, status=LeaveStatus.APPROVED),
        LeaveRequest(student_id=ws, start_date=now - timedelta(days=10), end_date=now - timedelta(days=9), reason="参加婚礼", leave_type=LeaveType.PERSONAL, status=LeaveStatus.PENDING),
        LeaveRequest(student_id=ws, start_date=now + timedelta(days=15), end_date=now + timedelta(days=17), reason="外出实习面试", leave_type=LeaveType.PERSONAL, status=LeaveStatus.PENDING),
    ]

    db.add_all(leaves)
    db.commit()

# ─── 办事工单（测试服务审批流）─────────────────────────────────
if db.query(ServiceTicket).count() == 0:
    now_date = date.today()
    tickets = []

    zs = sid("2024001")
    tickets += [
        ServiceTicket(applicant_id=zs, applicant_name="张三", applicant_no="2024001", applicant_college="软件学院", type=TicketType.CERTIFICATE, title="在校证明", content="实习求职需要在校证明", status=TicketStatus.PENDING),
    ]

    ls = sid("2024002")
    tickets += [
        ServiceTicket(applicant_id=ls, applicant_name="李四", applicant_no="2024002", applicant_college="软件学院", type=TicketType.PROJECT, title="科研项目立项", content="基于机器学习的校园助手优化研究", status=TicketStatus.APPROVED),
        ServiceTicket(applicant_id=ls, applicant_name="李四", applicant_no="2024002", applicant_college="软件学院", type=TicketType.CERTIFICATE, title="成绩单申请", content="考研需要", status=TicketStatus.PENDING),
    ]

    ws = sid("2024008")
    tickets += [
        ServiceTicket(applicant_id=ws, applicant_name="吴十", applicant_no="2024008", applicant_college="现代服务学院", type=TicketType.LEAVE, title="补假申请", content="上周五忘记请假，申请补假", status=TicketStatus.PENDING),
    ]

    db.add_all(tickets)
    db.commit()

# ─── 危机预警（测试AI监测 + 教师干预流）─────────────────────────
if db.query(AIDialogSummary).count() == 0:
    now = date.today()
    alerts = []

    # 李四 — 轻度危机
    ls = sid("2024002")
    alerts += [
        AIDialogSummary(student_id=ls, summary="学生表示近期学习压力大，有焦虑情绪，睡眠质量不佳", level=CrisisLevel.MILD, keywords_matched="焦虑,失眠", resolved=False),
        AIDialogSummary(student_id=ls, summary="学生在对话中提到对未来的迷茫，情绪低落", level=CrisisLevel.NORMAL, keywords_matched="迷茫", resolved=True),
    ]

    # 钱七 — 中重度危机（测试重点预警案例）
    qq = sid("2024005")
    alerts += [
        AIDialogSummary(student_id=qq, summary="学生多次提到失眠、焦虑，对考试感到极度恐慌，建议重点关注", level=CrisisLevel.MODERATE, keywords_matched="失眠,焦虑,考试", resolved=False),
        AIDialogSummary(student_id=qq, summary='学生表示"觉得活着没意思"，触发高危关键词，已立即通知辅导员', level=CrisisLevel.SEVERE, keywords_matched="没意思,活着", resolved=False),
    ]

    db.add_all(alerts)
    db.commit()


db.close()
print("Seed data created successfully")
print(f"Students: 2024001~2024009 (9 students)")
print(f"Teachers: t1001~t1007 (7 teachers)")
print(f"Tutor bindings: 陈慧敏→张三/赵六/郑十一, 张伟明→王五/钱七, etc.")
print(f"Test accounts: all use password '123456'")
print(f"Test scenarios: 全面型/挂科型/学霸型/竞赛型/危机型/新秀型/高材型/请假型/新入型")
