import request from '@/utils/request'
import type { GrowthRecord } from '@/types'

export interface GrowthProfile {
  total_score: number
  radar: { name: string; value: number }[]
  stats_by_type: { name: string; value: number }[]
  monthly_trend: { month: string; count: number; type: string }[]
  skills: string[]
  interests: string[]
  total_records: number
  total_skills: number
  gpa_trend: { semester: string; gpa: number }[]
}

export function getGrowthProfile() {
  return request.get<GrowthProfile>('/growth/profile')
}

export function getGrowthRecords(studentId?: number) {
  return request.get<GrowthRecord[]>('/growth/records', { params: { student_id: studentId } })
}

export function createGrowthRecord(data: Partial<GrowthRecord>) {
  return request.post<GrowthRecord>('/growth/records', data)
}

export function deleteGrowthRecord(id: number) {
  return request.delete(`/growth/records/${id}`)
}
