import json, re, httpx
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.academic import Course, Grade, Exam
from bs4 import BeautifulSoup
from app.models.leave import LeaveRequest
from app.models.growth import GrowthRecord, RecordType
from app.models.service import ServiceTicket, TicketType
from app.models.knowledge import KnowledgeItem
from app.models.campus import CampusScenery
from sqlalchemy import or_


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "create_leave",
            "description": "创建请假申请。当学生表达请假意图时（如'请假'、'想请假'、'参加比赛需要请假'等），提取信息并自动创建请假申请",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "请假开始日期，格式YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "请假结束日期，格式YYYY-MM-DD"},
                    "reason": {"type": "string", "description": "请假原因"},
                    "leave_type": {"type": "string", "enum": ["competition", "sick", "personal", "other"], "description": "请假类型"}
                },
                "required": ["start_date", "end_date", "reason", "leave_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_growth_record",
            "description": "创建成长记录。当学生提到获得了荣誉、竞赛获奖、取得奖项、参与实践时，自动调用此工具记录到成长档案",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "记录标题，如'挑战杯省赛二等奖'"},
                    "record_type": {"type": "string", "enum": ["honor", "competition", "award", "practice"], "description": "类型：honor荣誉/competition竞赛/award奖项/practice实践"},
                    "description": {"type": "string", "description": "详细描述"},
                    "date": {"type": "string", "description": "发生日期，格式YYYY-MM-DD，不清楚时可向学生询问"}
                },
                "required": ["title", "record_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "submit_service_request",
            "description": "提交办事服务申请（在校证明、调宿申请等）",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "申请标题"},
                    "content": {"type": "string", "description": "申请内容详情"},
                    "request_type": {"type": "string", "enum": ["certificate", "other"], "description": "申请类型"}
                },
                "required": ["title", "content", "request_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_schedule",
            "description": "查询学生的课程表信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "查询日期，格式YYYY-MM-DD，不传则查本周"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_grades",
            "description": "查询学生的成绩和GPA信息",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_exams",
            "description": "查询学生的考试安排",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_knowledge",
            "description": "查询校园知识库（办事流程、规章制度、校园导航等）",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "查询关键词"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_sceneries",
            "description": "查询校园风景信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "area": {"type": "string", "enum": ["anzhou", "youxian"], "description": "校区：anzhou安州/youxian游仙，不传则查全部"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_announcements",
            "description": "查询教务处官网最新通知公告（实时抓取）",
            "parameters": {"type": "object", "properties": {}}
        }
    },
]


async def execute_tool(name: str, args: dict, user: User) -> dict:
    db = SessionLocal()
    try:
        handler = {
            "create_leave": _create_leave,
            "create_growth_record": _create_growth_record,
            "submit_service_request": _submit_service_request,
            "query_schedule": _query_schedule,
            "query_grades": _query_grades,
            "query_exams": _query_exams,
            "query_knowledge": _query_knowledge,
            "query_sceneries": _query_sceneries,
        "query_announcements": _query_announcements,
        }
        fn = handler.get(name)
        if not fn:
            return {"error": f"未知工具: {name}"}
        return fn(db, args, user)
    finally:
        db.close()


def _create_leave(db: Session, args: dict, user: User) -> dict:
    leave = LeaveRequest(
        student_id=user.id,
        start_date=args["start_date"],
        end_date=args["end_date"],
        reason=args["reason"],
        leave_type=args.get("leave_type", "other"),
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    type_names = {"competition": "比赛", "sick": "病假", "personal": "事假", "other": "其他"}
    return {
        "success": True, "leave_id": leave.id,
        "start_date": str(leave.start_date), "end_date": str(leave.end_date),
        "reason": leave.reason, "leave_type": type_names.get(leave.leave_type, leave.leave_type),
        "status": "pending",
        "message": f"✅ 请假申请已提交！假期：{leave.start_date} 至 {leave.end_date}，原因：{leave.reason}。等待辅导员审批。"
    }


def _create_growth_record(db: Session, args: dict, user: User) -> dict:
    type_map = {"honor": RecordType.HONOR, "competition": RecordType.COMPETITION, "award": RecordType.AWARD, "practice": RecordType.PRACTICE}
    type_names = {"honor": "荣誉", "competition": "竞赛", "award": "奖项", "practice": "实践"}
    record = GrowthRecord(
        student_id=user.id,
        type=type_map.get(args["record_type"], RecordType.HONOR),
        title=args["title"],
        description=args.get("description", ""),
        date=args.get("date", "2026-01-01"),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {
        "success": True, "record_id": record.id,
        "title": record.title, "type": type_names.get(args["record_type"], args["record_type"]),
        "message": f"📝 已记录到成长档案：{record.title}"
    }


def _submit_service_request(db: Session, args: dict, user: User) -> dict:
    ticket = ServiceTicket(
        applicant_id=user.id,
        type=args.get("request_type", "other"),
        title=args["title"],
        content=args["content"],
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return {
        "success": True, "ticket_id": ticket.id,
        "message": f"📋 申请已提交（编号：{ticket.id}），等待审批。"
    }


def _query_schedule(db: Session, args: dict, user: User) -> dict:
    courses = db.query(Course).filter(Course.student_id == user.id).order_by(Course.day_of_week, Course.start_period).all()
    if not courses:
        return {"message": "暂无课表信息", "courses": []}
    day_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    result = []
    for c in courses:
        result.append({
            "name": c.name, "teacher": c.teacher, "location": c.location,
            "day": day_names[c.day_of_week - 1] if 1 <= c.day_of_week <= 7 else f"周{c.day_of_week}",
            "period": f"第{c.start_period}-{c.end_period}节",
            "weeks": f"第{c.week_start}-{c.week_end}周",
        })
    return {"message": f"共{len(result)}门课程", "courses": result}


def _query_grades(db: Session, args: dict, user: User) -> dict:
    grades = db.query(Grade).filter(Grade.student_id == user.id).order_by(Grade.semester.desc()).all()
    if not grades:
        return {"message": "暂无成绩信息", "grades": []}
    result = []
    total_credits = 0
    total_weighted = 0.0
    for g in grades:
        result.append({"course_name": g.course_name, "score": g.score, "credit": g.credit, "gpa": g.gpa, "semester": g.semester})
        total_credits += g.credit
        total_weighted += g.gpa * g.credit
    avg_gpa = round(total_weighted / total_credits, 2) if total_credits > 0 else 0
    return {"message": f"共{len(result)}门课程，平均GPA：{avg_gpa}", "grades": result, "avg_gpa": avg_gpa}


def _query_exams(db: Session, args: dict, user: User) -> dict:
    exams = db.query(Exam).filter(Exam.student_id == user.id).order_by(Exam.exam_date).all()
    if not exams:
        return {"message": "暂无考试安排", "exams": []}
    result = []
    for e in exams:
        result.append({"course_name": e.course_name, "exam_date": str(e.exam_date), "start_time": str(e.start_time), "end_time": str(e.end_time), "location": e.location})
    return {"message": f"共{len(result)}门考试", "exams": result}


def _query_knowledge(db: Session, args: dict, user: User) -> dict:
    query = args.get("query", "")
    items = db.query(KnowledgeItem).filter(
        or_(KnowledgeItem.question.like(f"%{query}%"), KnowledgeItem.answer.like(f"%{query}%"), KnowledgeItem.tags.like(f"%{query}%"))
    ).limit(5).all()
    if not items:
        return {"message": "未找到相关信息", "items": []}
    return {"message": f"找到{len(items)}条相关信息", "items": [{"category": i.category, "question": i.question, "answer": i.answer} for i in items]}


def _query_sceneries(db: Session, args: dict, user: User) -> dict:
    query = db.query(CampusScenery)
    if args.get("area"):
        query = query.filter(CampusScenery.area == args["area"])
    items = query.all()
    if not items:
        return {"message": "暂无风景信息", "sceneries": []}
    return {"message": f"共{len(items)}个景点", "sceneries": [{"title": s.title, "description": s.description, "location": s.location} for s in items]}


def _query_announcements(db: Session, args: dict, user: User) -> dict:
    import httpx, re
    from bs4 import BeautifulSoup
    try:
        resp = httpx.get("https://jwc.mycc.edu.cn/jwgl/tzgg.htm", timeout=10, follow_redirects=True)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
        items = []
        for li in soup.find_all("li"):
            a = li.find("a")
            if not a: continue
            href = a.get("href", "")
            if "info/1011/" not in href: continue
            text = a.get_text(strip=True)
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})$", text)
            date = date_match.group(1) if date_match else None
            title = text[:-10] if date else text
            items.append({"title": title, "date": date})
        return {"message": f"教务处最新通知（共{len(items)}条）", "announcements": items[:10]}
    except Exception as e:
        return {"message": "通知获取失败", "announcements": []}
