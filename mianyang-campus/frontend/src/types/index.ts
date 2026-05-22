export type UserRole = 'student' | 'teacher' | 'admin'

export interface UserInfo {
  id: number
  username: string
  name: string
  role: UserRole
  college?: string
  avatar?: string
  skills_json?: { skills: { name: string; context: string }[]; interests: string[] }
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  suggestions?: Suggestion[]
  leaveData?: LeaveRequestOut
  timestamp: string
}

export interface Suggestion {
  text: string
  link?: string
  action?: string
}

export interface LeaveRequestCreate {
  start_date: string
  end_date: string
  reason: string
  leave_type: string
}

export interface LeaveRequestOut {
  id: number
  student_id: number
  student_name: string
  start_date: string
  end_date: string
  reason: string
  leave_type: string
  status: string
  reject_reason: string | null
  created_at: string
}

export interface CrisisAlert {
  id: number
  student_id: number
  student_name: string
  summary: string
  level: string
  keywords_matched: string | null
  resolved: boolean
  created_at: string
}

export interface GrowthRecord {
  id: number
  student_id: number
  type: 'honor' | 'competition' | 'award' | 'practice'
  title: string
  description: string
  date: string
  attachment_url?: string
}

export interface CampusFigure {
  id: number
  name: string
  title: string
  avatar: string
  description: string
  category: 'student' | 'teacher' | 'alumni'
}

export interface CampusScenery {
  id: number
  title: string
  image_url: string
  description: string
  location: string
  area: string
}

export interface Announcement {
  title: string
  date: string | null
  url: string | null
}

export interface Course {
  id: number
  name: string
  teacher: string
  location: string
  day_of_week: number
  start_period: number
  end_period: number
  week_start: number
  week_end: number
}

export interface Grade {
  id: number
  course_name: string
  score: number
  credit: number
  gpa: number
  semester: string
}

export interface Exam {
  id: number
  course_name: string
  exam_date: string
  start_time: string
  end_time: string
  location: string
}

export interface ServiceTicket {
  id: number
  type: string
  title: string
  content: string
  status: string
  created_at: string
}
