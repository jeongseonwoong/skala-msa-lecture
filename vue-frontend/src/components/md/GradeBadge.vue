<template>
  <span class="grade-badge" :class="`grade-${meta.cls}`">
    <span class="grade-dot"></span>{{ meta.label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { GRADE_META } from '@/constants/evaluation.js'

const props = defineProps({
  grade: { type: String, required: true }
})

const meta = computed(() => GRADE_META[props.grade] || { label: props.grade, cls: 'insufficient' })
</script>

<style scoped>
.grade-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}
.grade-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.grade-excellent { background: var(--color-success-light); color: var(--color-success); }
.grade-excellent .grade-dot { background: var(--color-success); }
.grade-warning { background: var(--color-warning-light); color: var(--color-warning); }
.grade-warning .grade-dot { background: var(--color-warning); }
.grade-review { background: var(--color-danger-light); color: var(--color-danger); }
.grade-review .grade-dot { background: var(--color-danger); }
.grade-insufficient { background: var(--color-neutral-light); color: var(--color-neutral); }
.grade-insufficient .grade-dot { background: var(--color-neutral); }
</style>
