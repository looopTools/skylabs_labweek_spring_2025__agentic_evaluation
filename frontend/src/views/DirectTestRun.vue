<template>
  <div class="direct-test-run">
    <h1>Direct Test Run</h1>
    
    <div class="test-run-header">
      <div v-if="loading" class="loading">Loading template...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="!template" class="empty">Template not found</div>
      <div v-else class="template-info">
        <h2>{{ template.name }}</h2>
        <p v-if="template.description">{{ template.description }}</p>
        <div class="template-meta">
          <span class="template-type">{{ template.field || 'Custom' }}</span>
          <span class="test-case-count">{{ testCases.length }} Test Cases</span>
        </div>
      </div>
      
      <div class="test-run-controls">
        <button @click="saveTestRun" class="btn primary" :disabled="!canSave">Save Test Run</button>
        <button @click="cancelTestRun" class="btn">Cancel</button>
      </div>
    </div>
    
    <div class="test-run-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${completionPercentage}%` }"></div>
      </div>
      <div class="progress-stats">
        <span>{{ completedCount }} / {{ testCases.length }} completed</span>
        <span>{{ passCount }} passed, {{ failCount }} failed</span>
      </div>
    </div>
    
    <div class="test-cases-container">
      <div v-if="loading" class="loading">Loading test cases...</div>
      <div v-else-if="testCases.length === 0" class="empty">No test cases in this template</div>
      <div v-else class="test-cases-list">
        <div v-for="(testCase, index) in testCases" :key="testCase.id" class="test-case-card">
          <div class="test-case-header">
            <h3>{{ testCase.title }}</h3>
            <span class="test-case-id">{{ testCase.case_id ? testCase.case_id : testCase.id }}</span>
          </div>
          
          <div class="test-case-details">
            <p v-if="testCase.description">{{ testCase.description }}</p>
            
            <div v-if="testCase.steps" class="test-case-steps">
              <h4>Steps:</h4>
              <pre>{{ testCase.steps }}</pre>
            </div>
            
            <div v-if="testCase.precondition" class="test-case-precondition">
              <h4>Precondition:</h4>
              <pre>{{ testCase.precondition }}</pre>
            </div>
          </div>
          
          <div class="test-case-result">
            <div class="form-group">
              <label>Result:</label>
              <div class="result-buttons">
                <button 
                  @click="setResult(index, 'Pass')" 
                  :class="['btn', results[index].result === 'Pass' ? 'success' : '']"
                >
                  Pass
                </button>
                <button 
                  @click="setResult(index, 'Fail')" 
                  :class="['btn', results[index].result === 'Fail' ? 'danger' : '']"
                >
                  Fail
                </button>
                <button 
                  @click="setResult(index, 'Skip')" 
                  :class="['btn', results[index].result === 'Skip' ? 'warning' : '']"
                >
                  Skip
                </button>
              </div>
            </div>
            
            <div class="form-group">
              <label for="comment">Comment:</label>
              <textarea id="comment" v-model="results[index].comment" rows="2"></textarea>
            </div>
            
            <div class="form-group">
              <label for="logs">Logs:</label>
              <textarea id="logs" v-model="results[index].logs" rows="2"></textarea>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api'

export default {
  name: 'DirectTestRun',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    const templateId = route.params.id
    const loading = ref(true)
    const error = ref(null)
    const template = ref(null)
    const testCases = ref([])
    const results = ref([])
    
    onMounted(async () => {
      try {
        loading.value = true
        error.value = null
        
        // Fetch the template
        const templateResponse = await axios.get(`${API_URL}/test-run-templates/${templateId}`)
        template.value = templateResponse.data
        
        // Fetch the test cases for this template
        const testCasesResponse = await axios.get(`${API_URL}/test-run-templates/${templateId}/test-cases`)
        testCases.value = testCasesResponse.data
        
        // Initialize results array
        results.value = testCases.value.map(tc => ({
          test_case_id: tc.id,
          result: '',
          comment: '',
          logs: '',
          artifacts: ''
        }))
      } catch (err) {
        console.error('Error loading template:', err)
        error.value = (err.response && err.response.data && err.response.data.detail) || err.message || 'Failed to load template'
      } finally {
        loading.value = false
      }
    })
    
    const setResult = (index, result) => {
      results.value[index].result = result
    }
    
    const completedCount = computed(() => {
      return results.value.filter(r => r.result).length
    })
    
    const passCount = computed(() => {
      return results.value.filter(r => r.result === 'Pass').length
    })
    
    const failCount = computed(() => {
      return results.value.filter(r => r.result === 'Fail').length
    })
    
    const completionPercentage = computed(() => {
      if (testCases.value.length === 0) return 0
      return (completedCount.value / testCases.value.length) * 100
    })
    
    const canSave = computed(() => {
      return completedCount.value > 0
    })
    
    const saveTestRun = async () => {
      try {
        loading.value = true
        error.value = null
        
        // Create a new test run
        const testRunResponse = await axios.post(`${API_URL}/test-runs`, {
          status: 'Completed',
          operator_id: null // Would be set to the current user in a real app
        })
        
        const testRunId = testRunResponse.data.id
        
        // Create test case results
        const validResults = results.value.filter(r => r.result)
        for (const result of validResults) {
          await axios.post(`${API_URL}/test-case-results`, {
            ...result,
            test_run_id: testRunId
          })
        }
        
        alert(`Test run saved successfully with ID: ${testRunId}`)
        router.push('/test-runs')
      } catch (err) {
        console.error('Error saving test run:', err)
        error.value = (err.response && err.response.data && err.response.data.detail) || err.message || 'Failed to save test run'
      } finally {
        loading.value = false
      }
    }
    
    const cancelTestRun = () => {
      if (confirm('Are you sure you want to cancel this test run? All entered data will be lost.')) {
        router.push('/test-run-templates')
      }
    }
    
    return {
      loading,
      error,
      template,
      testCases,
      results,
      setResult,
      completedCount,
      passCount,
      failCount,
      completionPercentage,
      canSave,
      saveTestRun,
      cancelTestRun
    }
  }
}
</script>

<style scoped>
.direct-test-run {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.test-run-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.template-info {
  flex: 1;
}

.template-meta {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.template-type {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  background-color: #f5f5f5;
  color: #666;
}

.test-case-count {
  font-weight: bold;
  color: #42b983;
}

.test-run-controls {
  display: flex;
  gap: 0.5rem;
}

.test-run-progress {
  margin-bottom: 2rem;
}

.progress-bar {
  height: 0.5rem;
  background-color: #f5f5f5;
  border-radius: 0.25rem;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background-color: #42b983;
  transition: width 0.3s ease;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: #666;
}

.test-cases-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.test-case-card {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.test-case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.test-case-id {
  font-size: 0.875rem;
  color: #666;
  background-color: #f5f5f5;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.test-case-details {
  margin-bottom: 1.5rem;
}

.test-case-steps,
.test-case-precondition {
  margin-top: 1rem;
}

pre {
  background-color: #f5f5f5;
  padding: 0.75rem;
  border-radius: 0.25rem;
  white-space: pre-wrap;
  font-family: inherit;
  margin: 0.5rem 0;
}

.test-case-result {
  border-top: 1px solid #eee;
  padding-top: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
}

.result-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background-color: #e0e0e0;
}

.btn.primary {
  background-color: #42b983;
  color: white;
}

.btn.success {
  background-color: #4caf50;
  color: white;
}

.btn.danger {
  background-color: #f44336;
  color: white;
}

.btn.warning {
  background-color: #ff9800;
  color: white;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading, .error, .empty {
  text-align: center;
  padding: 2rem;
}

.error {
  color: #e53935;
}
</style>
