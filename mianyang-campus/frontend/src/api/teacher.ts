import request from '@/utils/request'

export interface StudentSummary {
  id: number
  name: string
  college: string | null
  username: string
  skills_json: { skills: { name: string; context: string }[]; interests: string[] } | null
  growth_count: number
  leave_count: number
  crisis_level: string | null
  latest_crisis_summary: string | null
  latest_crisis_time: string | null
}

export interface StudentDetail {
  id: number
  name: string
  college: string | null
  username: string
  skills_json: any
  growth_records: any[]
  crisis_alerts: any[]
  leave_requests: any[]
}

export function getStudents(search?: string) {
  const params = search ? { search } : {}
  return request.get<StudentSummary[]>('/teacher/students', { params })
}

export function getStudentDetail(id: number) {
  return request.get<StudentDetail>(`/teacher/students/${id}`)
}

export interface DashboardStats {
  total_students: number
  alert_count: number
  pending_leave_count: number
  severe_alert_count: number
  resolved_alert_count: number
}

export function getDashboardStats() {
  return request.get<DashboardStats>('/teacher/dashboard')
}
