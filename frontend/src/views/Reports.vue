<template>
  <div class="reports">
    <h1>Test Reports</h1>
    
    <div class="report-filters">
      <div class="filter-group">
        <label for="report-type">Report Type:</label>
        <select id="report-type" v-model="reportType">
          <option value="latest">Latest Test Runs</option>
          <option value="release">Release Test Run</option>
          <option value="regression">Regression Test Run</option>
        </select>
      </div>
    </div>
    
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="report-content">
      <div v-if="reportType === 'latest'" class="latest-runs">
        <h2>Latest Test Runs Comparison</h2>
        
        <div v-if="latestTestRuns.length < 2" class="empty">
          Not enough test runs to compare. Need at least 2 test runs.
          <div class="create-run-prompt">
            <p>You need at least two test runs to compare results.</p>
            <button @click="reportType = 'release'" class="btn primary">Create Release Test Run</button>
            <button @click="reportType = 'regression'" class="btn secondary">Create Regression Test Run</button>
          </div>
        </div>
        <div v-else class="comparison-view">
          <div class="test-run-tables">
            <div v-for="run in latestTestRuns" :key="run.id" class="test-run-column">
              <div class="test-run-header">
                <h3>Test Run #{{ run.id }}</h3>
                <div class="test-run-meta">
                  <span class="status-badge" :class="run.status.toLowerCase().replace(' ', '-')">{{ run.status }}</span>
                  <span class="operator">{{ getOperatorName(run.operator_id) }}</span>
                </div>
                <div class="test-run-summary">
                  <div class="summary-item pass">
                    <span class="count">{{ getPassCount(run.id) }}</span>
                    <span class="label">Pass</span>
                  </div>
                  <div class="summary-item fail">
                    <span class="count">{{ getFailCount(run.id) }}</span>
                    <span class="label">Fail</span>
                  </div>
                  <div class="summary-item total">
                    <span class="count">{{ getResultsForRun(run.id).length }}</span>
                    <span class="label">Total</span>
                  </div>
                </div>
              </div>
              
              <table>
                <thead>
                  <tr>
                    <th>Test Case ID</th>
                    <th>Result</th>
                    <th>Comments</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="result in getResultsForRun(run.id)" :key="result.id">
                    <td>{{ getTestCaseName(result.test_case_id) }}</td>
                    <td :class="result.result.toLowerCase()">{{ result.result }}</td>
                    <td>{{ result.comment || '-' }}</td>
                    <td>
                      <button @click="editResult(result)" class="btn small">Edit</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <div class="chart-container">
            <h3>Pass/Fail Results</h3>
            <div class="chart-placeholder">
              <!-- Chart.js would be implemented here -->
              <div class="bar-chart">
                <div v-for="run in latestTestRuns" :key="run.id" class="chart-column">
                  <div class="chart-label">Run #{{ run.id }}</div>
                  <div class="chart-bars">
                    <div class="bar pass" :style="{ height: getPassPercentage(run.id) + '%' }">
                      {{ getPassCount(run.id) }} Pass
                    </div>
                    <div class="bar fail" :style="{ height: getFailPercentage(run.id) + '%' }">
                      {{ getFailCount(run.id) }} Fail
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else-if="reportType === 'release'" class="release-run">
        <h2>Release Test Run</h2>
        <div class="predefined-run-container">
          <div class="test-cases-selection">
            <h3>Test Cases</h3>
            <div class="search-box">
              <input type="text" v-model="searchQuery" placeholder="Search test cases...">
            </div>
            <div class="test-cases-list">
              <div v-for="testCase in filteredTestCases" :key="testCase.id" class="test-case-item">
                <div class="test-case-info">
                  <strong>{{ testCase.id }}</strong>: {{ testCase.title }}
                </div>
                <button 
                  @click="addToReleaseRun(testCase)" 
                  class="btn small"
                  :disabled="isInReleaseRun(testCase.id)"
                >
                  {{ isInReleaseRun(testCase.id) ? 'Added' : 'Add' }}
                </button>
              </div>
            </div>
          </div>
          
          <div class="selected-test-cases">
            <h3>Selected Test Cases</h3>
            <div v-if="releaseRunTestCases.length === 0" class="empty">
              No test cases selected for release run
            </div>
            <div v-else class="selected-list">
              <div v-for="testCase in releaseRunTestCases" :key="testCase.id" class="selected-item">
                <div class="test-case-info">
                  <strong>{{ testCase.id }}</strong>: {{ testCase.title }}
                </div>
                <div class="result-input">
                  <select v-model="testCase.result">
                    <option value="Pass">Pass</option>
                    <option value="Fail">Fail</option>
                    <option value="N/A">N/A</option>
                  </select>
                </div>
                <div class="comment-input">
                  <input type="text" v-model="testCase.comment" placeholder="Add comment...">
                </div>
                <button @click="removeFromReleaseRun(testCase.id)" class="btn small danger">
                  Remove
                </button>
              </div>
            </div>
            <div class="actions">
              <button @click="saveReleaseRun" class="btn primary" :disabled="releaseRunTestCases.length === 0">
                Save Release Run
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else-if="reportType === 'regression'" class="regression-run">
        <h2>Regression Test Run</h2>
        <div class="predefined-run-container">
          <div class="test-cases-selection">
            <h3>Test Cases</h3>
            <div class="search-box">
              <input type="text" v-model="regressionSearchQuery" placeholder="Search test cases...">
            </div>
            <div class="test-cases-list">
              <div v-for="testCase in filteredRegressionTestCases" :key="testCase.id" class="test-case-item">
                <div class="test-case-info">
                  <strong>{{ testCase.id }}</strong>: {{ testCase.title }}
                </div>
                <button 
                  @click="addToRegressionRun(testCase)" 
                  class="btn small"
                  :disabled="isInRegressionRun(testCase.id)"
                >
                  {{ isInRegressionRun(testCase.id) ? 'Added' : 'Add' }}
                </button>
              </div>
            </div>
          </div>
          
          <div class="selected-test-cases">
            <h3>Selected Test Cases</h3>
            <div v-if="regressionRunTestCases.length === 0" class="empty">
              No test cases selected for regression run
            </div>
            <div v-else class="selected-list">
              <div v-for="testCase in regressionRunTestCases" :key="testCase.id" class="selected-item">
                <div class="test-case-info">
                  <strong>{{ testCase.id }}</strong>: {{ testCase.title }}
                </div>
                <div class="result-input">
                  <select v-model="testCase.result">
                    <option value="Pass">Pass</option>
                    <option value="Fail">Fail</option>
                    <option value="N/A">N/A</option>
                  </select>
                </div>
                <div class="comment-input">
                  <input type="text" v-model="testCase.comment" placeholder="Add comment...">
                </div>
                <button @click="removeFromRegressionRun(testCase.id)" class="btn small danger">
                  Remove
                </button>
              </div>
            </div>
            <div class="actions">
              <button @click="saveRegressionRun" class="btn primary" :disabled="regressionRunTestCases.length === 0">
                Save Regression Run
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Edit Result Modal -->
    <div v-if="showEditModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Edit Test Result</h3>
        <div v-if="editingResult" class="edit-form">
          <div class="form-group">
            <label for="result">Result:</label>
            <select id="result" v-model="editingResult.result">
              <option value="Pass">Pass</option>
              <option value="Fail">Fail</option>
              <option value="N/A">N/A</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="comment">Comment:</label>
            <textarea id="comment" v-model="editingResult.comment" rows="3"></textarea>
          </div>
          
          <div class="modal-actions">
            <button @click="saveEditedResult" class="btn primary">Save</button>
            <button @click="showEditModal = false" class="btn">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api'

export default {
  name: 'Reports',
  setup() {
    const store = useStore()
    const reportType = ref('latest')
    const searchQuery = ref('')
    const regressionSearchQuery = ref('')
    const releaseRunTestCases = ref([])
    const regressionRunTestCases = ref([])
    const editingResult = ref(null)
    const showEditModal = ref(false)
    
    // Mock data for operators until we implement that endpoint
    const testOperators = ref([
      { id: 1, name: 'John Doe' },
      { id: 2, name: 'Jane Smith' }
    ])
    
    onMounted(() => {
      store.dispatch('fetchTestRuns')
      store.dispatch('fetchTestCases')
      store.dispatch('fetchTestCaseResults')
    })
    
    const testRuns = computed(() => store.state.testRuns)
    const testCases = computed(() => store.state.testCases)
    const testCaseResults = computed(() => store.state.testCaseResults)
    const loading = computed(() => store.state.loading)
    const error = computed(() => store.state.error)
    
    const latestTestRuns = computed(() => {
      return testRuns.value
        .slice()
        .sort((a, b) => b.id - a.id)
        .slice(0, 2)
    })
    
    const filteredTestCases = computed(() => {
      if (!searchQuery.value) return testCases.value
      const query = searchQuery.value.toLowerCase()
      return testCases.value.filter(tc => 
        (tc.id && tc.id.toString().toLowerCase().includes(query)) || 
        (tc.title && tc.title.toLowerCase().includes(query)) ||
        (tc.area && tc.area.toLowerCase().includes(query))
      )
    })
    
    const filteredRegressionTestCases = computed(() => {
      if (!regressionSearchQuery.value) return testCases.value
      const query = regressionSearchQuery.value.toLowerCase()
      return testCases.value.filter(tc => 
        (tc.id && tc.id.toString().toLowerCase().includes(query)) || 
        (tc.title && tc.title.toLowerCase().includes(query)) ||
        (tc.area && tc.area.toLowerCase().includes(query))
      )
    })
    
    const getResultsForRun = (runId) => {
      return testCaseResults.value.filter(result => result.test_run_id === runId)
    }
    
    const getTestCaseName = (testCaseId) => {
      const testCase = testCases.value.find(tc => tc.id === testCaseId)
      return testCase ? testCase.id : `Unknown (${testCaseId})`
    }
    
    const getOperatorName = (operatorId) => {
      if (!operatorId) return 'No Operator'
      const operator = testOperators.value.find(op => op.id === operatorId)
      return operator ? operator.name : `Operator #${operatorId}`
    }
    
    const editResult = (result) => {
      editingResult.value = { ...result }
      showEditModal.value = true
    }
    
    const saveEditedResult = async () => {
      try {
        await axios.patch(`${API_URL}/test-case-results/${editingResult.value.id}`, {
          result: editingResult.value.result,
          comment: editingResult.value.comment
        })
        
        // Refresh data
        store.dispatch('fetchTestCaseResults')
        
        // Close modal
        showEditModal.value = false
        editingResult.value = null
      } catch (error) {
        console.error('Error updating test result:', error)
        store.commit('SET_ERROR', error.message || 'Failed to update test result')
      }
    }
    
    const getPassCount = (runId) => {
      return getResultsForRun(runId).filter(result => 
        result.result.toLowerCase() === 'pass'
      ).length
    }
    
    const getFailCount = (runId) => {
      return getResultsForRun(runId).filter(result => 
        result.result.toLowerCase() === 'fail'
      ).length
    }
    
    const getPassPercentage = (runId) => {
      const results = getResultsForRun(runId)
      if (results.length === 0) return 0
      return (getPassCount(runId) / results.length) * 100
    }
    
    const getFailPercentage = (runId) => {
      const results = getResultsForRun(runId)
      if (results.length === 0) return 0
      return (getFailCount(runId) / results.length) * 100
    }
    
    // Release Run functions
    const addToReleaseRun = (testCase) => {
      if (!isInReleaseRun(testCase.id)) {
        releaseRunTestCases.value.push({
          ...testCase,
          result: 'Pass',
          comment: ''
        })
      }
    }
    
    const removeFromReleaseRun = (testCaseId) => {
      releaseRunTestCases.value = releaseRunTestCases.value.filter(tc => tc.id !== testCaseId)
    }
    
    const isInReleaseRun = (testCaseId) => {
      return releaseRunTestCases.value.some(tc => tc.id === testCaseId)
    }
    
    const saveReleaseRun = async () => {
      try {
        // Create a new test run
        const testRunResponse = await axios.post(`${API_URL}/test-runs`, {
          status: 'Completed',
          operator_id: null
        })
        
        const testRunId = testRunResponse.data.id
        
        // Create test case results for each selected test case
        const results = releaseRunTestCases.value.map(tc => ({
          test_case_id: tc.id,
          test_run_id: testRunId,
          result: tc.result,
          comment: tc.comment,
          logs: '',
          artifacts: ''
        }))
        
        // Submit all results
        for (const result of results) {
          await axios.post(`${API_URL}/test-case-results`, result)
        }
        
        // Reset the form
        releaseRunTestCases.value = []
        
        // Refresh data
        store.dispatch('fetchTestRuns')
        store.dispatch('fetchTestCaseResults')
        
        // Switch to latest view to see the results
        reportType.value = 'latest'
      } catch (error) {
        console.error('Error saving release run:', error)
        store.commit('SET_ERROR', error.message || 'Failed to save release run')
      }
    }
    
    // Regression Run functions
    const addToRegressionRun = (testCase) => {
      if (!isInRegressionRun(testCase.id)) {
        regressionRunTestCases.value.push({
          ...testCase,
          result: 'Pass',
          comment: ''
        })
      }
    }
    
    const removeFromRegressionRun = (testCaseId) => {
      regressionRunTestCases.value = regressionRunTestCases.value.filter(tc => tc.id !== testCaseId)
    }
    
    const isInRegressionRun = (testCaseId) => {
      return regressionRunTestCases.value.some(tc => tc.id === testCaseId)
    }
    
    const saveRegressionRun = async () => {
      try {
        // Create a new test run
        const testRunResponse = await axios.post(`${API_URL}/test-runs`, {
          status: 'Completed',
          operator_id: null
        })
        
        const testRunId = testRunResponse.data.id
        
        // Create test case results for each selected test case
        const results = regressionRunTestCases.value.map(tc => ({
          test_case_id: tc.id,
          test_run_id: testRunId,
          result: tc.result,
          comment: tc.comment,
          logs: '',
          artifacts: ''
        }))
        
        // Submit all results
        for (const result of results) {
          await axios.post(`${API_URL}/test-case-results`, result)
        }
        
        // Reset the form
        regressionRunTestCases.value = []
        
        // Refresh data
        store.dispatch('fetchTestRuns')
        store.dispatch('fetchTestCaseResults')
        
        // Switch to latest view to see the results
        reportType.value = 'latest'
      } catch (error) {
        console.error('Error saving regression run:', error)
        store.commit('SET_ERROR', error.message || 'Failed to save regression run')
      }
    }
    
    return {
      reportType,
      testRuns,
      testCases,
      testCaseResults,
      loading,
      error,
      latestTestRuns,
      searchQuery,
      regressionSearchQuery,
      filteredTestCases,
      filteredRegressionTestCases,
      releaseRunTestCases,
      regressionRunTestCases,
      editingResult,
      showEditModal,
      testOperators,
      getResultsForRun,
      getTestCaseName,
      getOperatorName,
      getPassCount,
      getFailCount,
      getPassPercentage,
      getFailPercentage,
      addToReleaseRun,
      removeFromReleaseRun,
      isInReleaseRun,
      saveReleaseRun,
      addToRegressionRun,
      removeFromRegressionRun,
      isInRegressionRun,
      saveRegressionRun,
      editResult,
      saveEditedResult
    }
  }
}
</script>

<style scoped>
.reports {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.report-filters {
  margin-bottom: 2rem;
  background-color: #f5f5f5;
  padding: 1rem;
  border-radius: 8px;
}

.filter-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

select {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 100%;
  max-width: 300px;
}

.comparison-view {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.test-run-tables {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
}

.test-run-column {
  flex: 1;
  min-width: 300px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
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

.pass {
  background-color: rgba(66, 185, 131, 0.2);
  color: #2c7a57;
}

.fail {
  background-color: rgba(229, 57, 53, 0.2);
  color: #b71c1c;
}

.chart-container {
  margin-top: 2rem;
}

.chart-placeholder {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 1.5rem;
  height: 300px;
}

.bar-chart {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  height: 100%;
  gap: 2rem;
}

.chart-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100px;
}

.chart-label {
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.chart-bars {
  display: flex;
  flex-direction: column-reverse;
  width: 100%;
  height: 200px;
}

.bar {
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  padding: 0.5rem;
  transition: height 0.3s ease;
}

.bar.pass {
  background-color: #42b983;
}

.bar.fail {
  background-color: #e53935;
}

.loading, .error, .empty {
  text-align: center;
  padding: 2rem;
}

.error {
  color: #e53935;
}

.predefined-run-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.test-cases-selection,
.selected-test-cases {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-box {
  margin-bottom: 1rem;
}

.search-box input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.test-cases-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.test-case-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-bottom: 1px solid #ddd;
  background-color: white;
}

.test-case-item:last-child {
  border-bottom: none;
}

.test-case-info {
  flex: 1;
  text-align: left;
}

.selected-list {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.selected-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-bottom: 1px solid #ddd;
  background-color: white;
  gap: 1rem;
}

.selected-item:last-child {
  border-bottom: none;
}

.result-input select,
.comment-input input {
  padding: 0.25rem 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.comment-input {
  flex: 1;
}

.comment-input input {
  width: 100%;
}

.actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
}

.create-run-prompt {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: #f5f5f5;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.create-run-prompt p {
  margin-bottom: 1rem;
}

.test-run-header {
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.test-run-meta {
  display: flex;
  justify-content: space-between;
  margin: 0.5rem 0;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-badge.completed {
  background-color: #4caf50;
  color: white;
}

.status-badge.in-progress {
  background-color: #2196f3;
  color: white;
}

.status-badge.not-started {
  background-color: #9e9e9e;
  color: white;
}

.status-badge.aborted {
  background-color: #f44336;
  color: white;
}

.test-run-summary {
  display: flex;
  justify-content: space-around;
  margin-top: 1rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.summary-item .count {
  font-size: 1.5rem;
  font-weight: bold;
}

.summary-item .label {
  font-size: 0.8rem;
  color: #666;
}

.summary-item.pass .count {
  color: #4caf50;
}

.summary-item.fail .count {
  color: #f44336;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.edit-form {
  margin-top: 1rem;
}

.modal-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
}

@media (min-width: 768px) {
  .comparison-view {
    flex-direction: row;
  }
  
  .test-run-tables {
    flex: 2;
  }
  
  .chart-container {
    flex: 1;
    margin-top: 0;
  }
  
  .predefined-run-container {
    flex-direction: row;
  }
  
  .test-cases-selection,
  .selected-test-cases {
    flex: 1;
  }
}
</style>
