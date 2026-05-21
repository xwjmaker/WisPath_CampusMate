import request from '@/utils/request'
import type { GrowthRecord } from '@/types'

export function getGrowthRecords(studentId?: number) {
  return request.get<GrowthRecord[]>('/growth/records', { params: { student_id: studentId } })
}

export function createGrowthRecord(data: Partial<GrowthRecord>) {
  return request.post<GrowthRecord>('/growth/records', data)
}

export function deleteGrowthRecord(id: number) {
  return request.delete(`/growth/records/${id}`)
}
