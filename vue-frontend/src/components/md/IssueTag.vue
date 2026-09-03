<template>
  <span class="issue-tag" :class="`level-${level}`" :title="issue.detail">
    <span class="issue-icon">{{ meta.icon }}</span>{{ meta.label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { ISSUE_META, severityLevel } from '@/constants/evaluation.js'

const props = defineProps({
  issue: { type: Object, required: true }
})

const meta = computed(() => ISSUE_META[props.issue.type] || { label: props.issue.type, icon: '❗' })
const level = computed(() => severityLevel(props.issue.severity))
</script>

<style scoped>
.issue-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
  cursor: default;
}
.level-high { background: var(--color-danger-light); color: var(--color-danger); }
.level-mid  { background: var(--color-warning-light); color: var(--color-warning); }
.level-low  { background: var(--color-bg-tertiary); color: var(--color-text-secondary); }
</style>
