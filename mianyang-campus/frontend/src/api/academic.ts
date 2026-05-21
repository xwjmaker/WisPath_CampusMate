import request from '@/utils/request'
import type { Course, Grade, Exam } from '@/types'

export function getCourses() { return request.get<Course[]>('/academic/courses') }
export function getGrades() { return request.get<Grade[]>('/academic/grades') }
export function getExams() { return request.get<Exam[]>('/academic/exams') }
