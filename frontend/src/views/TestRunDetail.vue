<template>
  <div class="test-run-detail">
    <div class="header">
      <h1>Test Run #{{ testRunId }}</h1>
      <button @click="goBack" class="btn secondary">Back to Test Runs</button>
    </div>
    
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="!testRun" class="empty">Test run not found</div>
    <div v-else class="test-run-content">
      <div class="test-run-info">
        <h2>Test Run Information</h2>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">Status:</span>
            <span class="value">{{ testRun.status }}</span>
          </div>
          <div class="info-item">
            <span class="label">Operator:</span>
            <span class="value">{{ testRun.operator_id || 'None' }}</span>
          </div>
          <div class="info-item">
            <span class="label">Created:</span>
            <span class="value">{{ formatDate(testRun.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="label">Updated:</span>
            <span class="value">{{ formatDate(testRun.updated_at) }}</span>
          </div>
        </div>
      </div>
      
      <div class="test-results">
        <h2>Test Case Results</h2>
        <div v-if="!testRun.test_case_results || testRun.test_case_results.length === 0" class="empty">No test results available</div>
        <table v-else>
          <thead>
            <tr>
              <th>Test Case ID</th>
              <th>Result</th>
              <th>Comment</th>
              <th>Artifacts</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="result in testRun.test_case_results" :key="result.id">
              <td>{{ result.test_case_id }}</td>
              <td :class="getResultClass(result.result)">{{ result.result }}</td>
              <td>{{ result.comment || '-' }}</td>
              <td>{{ result.artifacts || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'

export default {
  name: 'TestRunDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const store = useStore()
    
    const testRunId = computed(() => route.params.id)
    const testRun = computed(() => store.state.currentTestRun)
    const testResults = computed(() => store.state.testCaseResults)
    const loading = computed(() => store.state.loading)
    const error = computed(() => store.state.error)
    
    onMounted(() => {
      store.dispatch('fetchTestRun', testRunId.value)
      // We don't need to fetch test case results separately as they're included in the test run
    })
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      try {
        const date = new Date(dateString)
        return date.toLocaleString()
      } catch (e) {
        return dateString || 'N/A'
      }
    }
    
    const getResultClass = (result) => {
      if (result === 'Pass') return 'result-pass'
      if (result === 'Fail') return 'result-fail'
      if (result === 'Skip') return 'result-skip'
      return ''
    }
    
    const goBack = () => {
      router.push('/test-runs')
    }
    
    return {
      testRunId,
      testRun,
      testResults,
      loading,
      error,
      formatDate,
      getResultClass,
      goBack
    }
  }
}
</script>

<style scoped>
.test-run-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background-color: #e0e0e0;
}

.btn.secondary {
  background-color: #4285f4;
  color: white;
}

.test-run-info {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.info-item {
  margin-bottom: 0.5rem;
}

.label {
  font-weight: bold;
  margin-right: 0.5rem;
}

.test-results {
  margin-top: 2rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f5f5f5;
  font-weight: bold;
}

tr:hover {
  background-color: #f5f5f5;
}

.result-pass {
  color: #4caf50;
  font-weight: bold;
}

.result-fail {
  color: #f44336;
  font-weight: bold;
}

.result-skip {
  color: #ff9800;
  font-weight: bold;
}

.loading, .error, .empty {
  text-align: center;
  padding: 2rem;
}

.error {
  color: #e53935;
}
</style>
