<template>
  <div class="test-runs">
    <h1>Test Runs</h1>
    
    <div class="actions">
      <button @click="showAddForm = !showAddForm" class="btn primary">
        {{ showAddForm ? 'Cancel' : 'Create Test Run' }}
      </button>
      <button @click="showUploadForm = !showUploadForm" class="btn secondary">
        {{ showUploadForm ? 'Cancel' : 'Upload Results' }}
      </button>
      <button @click="clearAllTestRuns" class="btn danger">
        Clear All Test Runs
      </button>
    </div>
    
    <div v-if="showAddForm" class="add-form">
      <h2>{{ isEditing ? 'Edit Test Run' : 'Create New Test Run' }}</h2>
      <form @submit.prevent="addTestRun">
        <div class="form-group">
          <label for="status">Status:</label>
          <select id="status" v-model="newTestRun.status" required>
            <option value="Not Started">Not Started</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
            <option value="Aborted">Aborted</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="operator_id">Operator:</label>
          <select id="operator_id" v-model="newTestRun.operator_id">
            <option value="">None</option>
            <option v-for="operator in testOperators" :key="operator.id" :value="operator.id">
              {{ operator.name }}
            </option>
          </select>
        </div>
        
        <button type="submit" class="btn primary">{{ isEditing ? 'Update Test Run' : 'Create Test Run' }}</button>
      </form>
    </div>
    
    <div v-if="showUploadForm" class="upload-form">
      <h2>Upload Test Results</h2>
      <div class="drag-drop-area" 
           :class="{ 'drag-over': isDragging }"
           @dragover.prevent="isDragging = true"
           @dragleave.prevent="isDragging = false"
           @drop.prevent="handleFileDrop">
        <div v-if="!uploadedFile">
          <i class="upload-icon">📁</i>
          <p>Drag and drop your test results file here</p>
          <p class="small">Supported formats: JSON, Excel (.xlsx)</p>
          <p>or</p>
          <label class="file-input-label">
            Browse Files
            <input type="file" @change="handleFileSelect" accept=".json,.xlsx" class="file-input">
          </label>
        </div>
        <div v-else class="file-preview">
          <p><strong>Selected file:</strong> {{ uploadedFile.name }}</p>
          <p><strong>Size:</strong> {{ formatFileSize(uploadedFile.size) }}</p>
          <div class="file-actions">
            <button @click="uploadFile" class="btn primary">Upload</button>
            <button @click="uploadedFile = null" class="btn">Cancel</button>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="testRuns.length === 0" class="empty">No test runs available</div>
    <div v-else class="test-runs-list">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Status</th>
            <th>Operator</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="run in testRuns" :key="run.id">
            <td>{{ run.id }}</td>
            <td>{{ run.status }}</td>
            <td>{{ run.operator_id || 'None' }}</td>
            <td>
              <button @click="viewTestRun(run.id)" class="btn small">View</button>
              <button @click="editTestRun(run.id)" class="btn small">Edit</button>
              <button @click="deleteTestRun(run.id)" class="btn small danger">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api'  // Make sure backend is running on this port

export default {
  name: 'TestRuns',
  setup() {
    const store = useStore()
    const router = useRouter()
    const showAddForm = ref(false)
    const showUploadForm = ref(false)
    const isDragging = ref(false)
    const uploadedFile = ref(null)
    const uploadStatus = ref('')
    const isEditing = ref(false)
    
    const newTestRun = ref({
      status: 'Not Started',
      operator_id: null
    })
    
    // Mock data for operators until we implement that endpoint
    const testOperators = ref([
      { id: 1, name: 'John Doe' },
      { id: 2, name: 'Jane Smith' }
    ])
    
    onMounted(() => {
      store.dispatch('fetchTestRuns')
      store.dispatch('fetchTestCaseResults')
    })
    
    const testRuns = computed(() => store.state.testRuns)
    const loading = computed(() => store.state.loading)
    const error = computed(() => store.state.error)
    
    const addTestRun = ref(async () => {
      try {
        await axios.post(`${API_URL}/test-runs`, newTestRun.value)
        // Reset form
        newTestRun.value = {
          status: 'Not Started',
          operator_id: null
        }
        showAddForm.value = false
        // Refresh the list
        store.dispatch('fetchTestRuns')
        alert('Test run created successfully')
      } catch (error) {
        console.error('Error adding test run:', error)
        store.commit('SET_ERROR', (error.response && error.response.data && error.response.data.detail) || error.message || 'Failed to add test run')
      }
    })
    
    const handleFileDrop = (event) => {
      isDragging.value = false
      const files = event.dataTransfer.files
      if (files.length > 0) {
        const file = files[0]
        if (isValidFileType(file)) {
          uploadedFile.value = file
        } else {
          store.commit('SET_ERROR', 'Invalid file type. Please upload JSON or Excel files only.')
        }
      }
    }
    
    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file && isValidFileType(file)) {
        uploadedFile.value = file
      } else if (file) {
        store.commit('SET_ERROR', 'Invalid file type. Please upload JSON or Excel files only.')
      }
    }
    
    const isValidFileType = (file) => {
      const validTypes = [
        'application/json',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ]
      return validTypes.includes(file.type) || 
             file.name.endsWith('.json') || 
             file.name.endsWith('.xlsx')
    }
    
    const formatFileSize = (bytes) => {
      if (bytes < 1024) return bytes + ' bytes'
      else if (bytes < 1048576) return (bytes / 1024).toFixed(2) + ' KB'
      else return (bytes / 1048576).toFixed(2) + ' MB'
    }
    
    const uploadFile = async () => {
      if (!uploadedFile.value) return
      
      const formData = new FormData()
      formData.append('file', uploadedFile.value)
      
      try {
        uploadStatus.value = 'uploading'
        store.commit('SET_LOADING', true)
        store.commit('SET_ERROR', null)
        
        // Use the correct endpoint for file uploads
        const response = await axios.post(`${API_URL}/test-runs/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        uploadStatus.value = 'success'
        uploadedFile.value = null
        showUploadForm.value = false
        
        // Refresh the test runs list
        await store.dispatch('fetchTestRuns')
        
        // Show success message with more details
        const message = `File uploaded successfully!\n\nTest run ID: ${response.data.test_run_id}\n\nPlease check the Test Suites and Test Cases tabs to see the imported data.`;
        alert(message);
        
        // Also refresh test suites and test cases
        await store.dispatch('fetchTestSuites')
        await store.dispatch('fetchTestCases')
      } catch (error) {
        uploadStatus.value = 'error'
        console.error('Error uploading file:', error)
        store.commit('SET_ERROR', (error.response && error.response.data && error.response.data.detail) || error.message || 'Failed to upload file')
      } finally {
        store.commit('SET_LOADING', false)
      }
    }
    
    const viewTestRun = (id) => {
      router.push(`/test-runs/${id}`)
    }
    
    const editTestRun = (id) => {
      // Find the test run to edit
      const testRun = testRuns.value.find(run => run.id === id)
      if (!testRun) return
      
      // Set up the form with current values
      newTestRun.value = {
        status: testRun.status,
        operator_id: testRun.operator_id
      }
      
      // Show the form and set editing mode
      showAddForm.value = true
      isEditing.value = true
      
      // Update the addTestRun function to handle both create and update
      addTestRun.value = async () => {
        try {
          await axios.put(`${API_URL}/test-runs/${id}`, newTestRun.value)
          // Reset form
          newTestRun.value = {
            status: 'Not Started',
            operator_id: null
          }
          showAddForm.value = false
          isEditing.value = false
          // Refresh the list
          store.dispatch('fetchTestRuns')
          alert('Test run updated successfully')
        } catch (error) {
          console.error('Error updating test run:', error)
          store.commit('SET_ERROR', (error.response && error.response.data && error.response.data.detail) || error.message || 'Failed to update test run')
        }
      }
    }
    
    const deleteTestRun = async (id) => {
      if (confirm('Are you sure you want to delete this test run?')) {
        try {
          store.commit('SET_LOADING', true)
          store.commit('SET_ERROR', null)
          
          // First delete all test case results associated with this test run
          const testCaseResults = store.state.testCaseResults.filter(
            result => result.test_run_id === id
          )
          
          for (const result of testCaseResults) {
            try {
              await axios.delete(`${API_URL}/test-case-results/${result.id}`)
            } catch (err) {
              console.warn(`Failed to delete test case result ${result.id}:`, err)
            }
          }
          
          // Then delete the test run itself
          await axios.delete(`${API_URL}/test-runs/${id}`)
          
          // Refresh the list
          await store.dispatch('fetchTestRuns')
          await store.dispatch('fetchTestCaseResults')
          
          // Show success message
          alert('Test run deleted successfully')
        } catch (error) {
          console.error('Error deleting test run:', error)
          store.commit('SET_ERROR', (error.response && error.response.data && error.response.data.detail) || error.message || 'Failed to delete test run')
        } finally {
          store.commit('SET_LOADING', false)
        }
      }
    }
    
    const clearAllTestRuns = async () => {
      if (confirm('Are you sure you want to delete ALL test runs and their results? This action cannot be undone.')) {
        try {
          store.commit('SET_LOADING', true)
          store.commit('SET_ERROR', null)
          
          // Call the backend endpoint to clear all test runs
          await axios.delete(`${API_URL}/test-runs/clear-all/`)
          
          // Refresh the lists
          await store.dispatch('fetchTestRuns')
          await store.dispatch('fetchTestCaseResults')
          await store.dispatch('fetchTestSuites')
          await store.dispatch('fetchTestCases')
          
          // Show success message
          alert('All test runs and results have been cleared successfully')
        } catch (error) {
          console.error('Error clearing test runs:', error)
          store.commit('SET_ERROR', (error.response && error.response.data && error.response.data.detail) || error.message || 'Failed to clear test runs')
        } finally {
          store.commit('SET_LOADING', false)
        }
      }
    }
    
    return {
      testRuns,
      testOperators,
      loading,
      error,
      showAddForm,
      showUploadForm,
      isDragging,
      uploadedFile,
      uploadStatus,
      newTestRun,
      addTestRun,
      handleFileDrop,
      handleFileSelect,
      formatFileSize,
      uploadFile,
      viewTestRun,
      editTestRun,
      deleteTestRun,
      clearAllTestRuns,
      isEditing
    }
  }
}
</script>

<style scoped>
.test-runs {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.actions {
  margin-bottom: 1rem;
  display: flex;
  justify-content: flex-end;
}

.add-form, .upload-form {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  max-width: 300px;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background-color: #e0e0e0;
  margin-right: 0.5rem;
}

.btn.primary {
  background-color: #42b983;
  color: white;
}

.btn.secondary {
  background-color: #4285f4;
  color: white;
}

.btn.danger {
  background-color: #e53935;
  color: white;
}

.btn.small {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
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

.loading, .error, .empty {
  text-align: center;
  padding: 2rem;
}

.error {
  color: #e53935;
}

/* Drag and drop styles */
.drag-drop-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
  background-color: #f9f9f9;
  cursor: pointer;
}

.drag-over {
  border-color: #42b983;
  background-color: rgba(66, 185, 131, 0.1);
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  display: block;
}

.file-input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

.file-input-label {
  display: inline-block;
  padding: 0.5rem 1rem;
  background-color: #42b983;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.file-preview {
  text-align: left;
}

.file-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.small {
  font-size: 0.8rem;
  color: #666;
}
</style>
