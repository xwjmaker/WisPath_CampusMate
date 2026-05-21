from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.campus import CampusFigure, CampusScenery, CampusArea
from app.models.academic import Course, Grade, Exam
from app.models.growth import GrowthRecord
from app.models.service import ServiceTicket
from app.models.knowledge import KnowledgeItem

Base.metadata.create_all(bind=engine)

db = SessionLocal()

if db.query(User).count() == 0:
    users = [
        User(username="2024001", password_hash=hash_password("123456"), name="张三", role=UserRole.STUDENT, college="软件学院"),
        User(username="2024002", password_hash=hash_password("123456"), name="李四", role=UserRole.STUDENT, college="软件学院"),
        User(username="t1001", password_hash=hash_password("123456"), name="王老师", role=UserRole.TEACHER, college="软件学院"),
        User(username="admin", password_hash=hash_password("admin123"), name="管理员", role=UserRole.ADMIN),
    ]
    db.add_all(users)
    db.commit()

if db.query(CampusFigure).count() == 0:
    figures = [
        CampusFigure(name="张三", title="2024年国家奖学金获得者", avatar="/images/avatar1.jpg", description="软件学院2022级学生，获得国家奖学金...", category="student"),
        CampusFigure(name="李四", title="ACM竞赛金牌得主", avatar="/images/avatar2.jpg", description="带领团队获得ICPC亚洲区域赛金牌...", category="student"),
        CampusFigure(name="王老师", title="优秀教师", avatar="/images/avatar3.jpg", description="软件学院副教授，主持多项省级课题...", category="teacher"),
    ]
    db.add_all(figures)
    db.commit()

if db.query(CampusScenery).count() == 0:
    sceneries = [
        CampusScenery(title="图书馆（安州）", image_url="/images/lib_anzhou.jpg", description="安州校区图书馆，现代化学习空间", location="校园中心", area=CampusArea.ANZHOU),
        CampusScenery(title="教学楼群（安州）", image_url="/images/teaching_anzhou.jpg", description="安州校区主教学区", location="校园东侧", area=CampusArea.ANZHOU),
        CampusScenery(title="校园湖景（安州）", image_url="/images/lake_anzhou.jpg", description="安州校区休闲景区", location="校园西侧", area=CampusArea.ANZHOU),
        CampusScenery(title="图书馆（游仙）", image_url="/images/lib_youxian.jpg", description="游仙校区图书馆", location="校园中心", area=CampusArea.YOUXIAN),
        CampusScenery(title="教学楼群（游仙）", image_url="/images/teaching_youxian.jpg", description="游仙校区主教学区", location="校园东侧", area=CampusArea.YOUXIAN),
        CampusScenery(title="校园林荫道（游仙）", image_url="/images/tree_youxian.jpg", description="游仙校区林荫大道", location="校园主干道", area=CampusArea.YOUXIAN),
    ]
    db.add_all(sceneries)
    db.commit()

if db.query(Course).count() == 0:
    courses = [
        Course(student_id=1, name="软件工程", teacher="王老师", location="教学楼301", day_of_week=1, start_period=1, end_period=2, week_start=1, week_end=16),
        Course(student_id=1, name="数据结构", teacher="赵老师", location="教学楼205", day_of_week=1, start_period=3, end_period=4, week_start=1, week_end=16),
        Course(student_id=1, name="操作系统", teacher="陈老师", location="教学楼302", day_of_week=3, start_period=1, end_period=2, week_start=1, week_end=16),
        Course(student_id=1, name="计算机网络", teacher="刘老师", location="实验楼401", day_of_week=5, start_period=5, end_period=6, week_start=1, week_end=16),
    ]
    db.add_all(courses)

if db.query(Grade).count() == 0:
    grades = [
        Grade(student_id=1, course_name="高等数学", score=85.0, credit=4.0, gpa=3.5, semester="2024-2025-1"),
        Grade(student_id=1, course_name="大学英语", score=78.0, credit=3.0, gpa=3.0, semester="2024-2025-1"),
        Grade(student_id=1, course_name="程序设计基础", score=92.0, credit=3.0, gpa=4.0, semester="2024-2025-1"),
    ]
    db.add_all(grades)

if db.query(KnowledgeItem).count() == 0:
    knowledge = [
        KnowledgeItem(category="办事流程", question="怎么请假", answer="请假流程：1. 登录系统 2. 进入办事服务页面 3. 选择请假申请 4. 填写请假类型、时间、理由 5. 提交后等待辅导员审批。你可以通过 [办事服务](/student/service) 页面提交申请。"),
        KnowledgeItem(category="办事流程", question="如何申请在校证明", answer="在校证明申请流程：1. 登录系统 2. 进入办事服务页面 3. 选择证明申请 4. 填写申请信息 5. 审批通过后可在电子版下载。"),
        KnowledgeItem(category="校园导航", question="图书馆在哪里", answer="图书馆位于校区中心位置，是校园地标建筑。你可以通过 [校园风采](/student/campus) 查看校园风景和导航。"),
        KnowledgeItem(category="规章制度", question="宿舍管理规定", answer="宿舍管理规定主要包括：1. 按时归寝 2. 禁止使用违规电器 3. 保持宿舍卫生 4. 贵重物品妥善保管。具体规定可咨询辅导员。"),
    ]
    db.add_all(knowledge)

db.close()
print("Seed data created successfully")
