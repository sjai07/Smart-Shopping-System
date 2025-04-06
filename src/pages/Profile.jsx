import React, { useState } from 'react'
import { Typography, Paper, Grid, TextField, Button, Chip, Box, FormControl, InputLabel, Select, MenuItem } from '@mui/material'
import axios from 'axios'

function Profile() {
  const [preferences, setPreferences] = useState({
    preferred_categories: [],
    price_range: [0, 1000],
    preferred_brands: []
  })

  const [newCategory, setNewCategory] = useState('')
  const [newBrand, setNewBrand] = useState('')
  const [loading, setLoading] = useState(false)

  const handleAddCategory = () => {
    if (newCategory && !preferences.preferred_categories.includes(newCategory)) {
      setPreferences(prev => ({
        ...prev,
        preferred_categories: [...prev.preferred_categories, newCategory]
      }))
      setNewCategory('')
    }
  }

  const handleAddBrand = () => {
    if (newBrand && !preferences.preferred_brands.includes(newBrand)) {
      setPreferences(prev => ({
        ...prev,
        preferred_brands: [...prev.preferred_brands, newBrand]
      }))
      setNewBrand('')
    }
  }

  const handleDeleteCategory = (category) => {
    setPreferences(prev => ({
      ...prev,
      preferred_categories: prev.preferred_categories.filter(c => c !== category)
    }))
  }

  const handleDeleteBrand = (brand) => {
    setPreferences(prev => ({
      ...prev,
      preferred_brands: prev.preferred_brands.filter(b => b !== brand)
    }))
  }

  const handleSavePreferences = async () => {
    try {
      setLoading(true)
      await axios.post('http://localhost:8000/recommendations/personalized', preferences)
      alert('Preferences saved successfully!')
    } catch (error) {
      console.error('Error saving preferences:', error)
      alert('Failed to save preferences. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Your Profile
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Shopping Preferences
            </Typography>

            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Preferred Categories
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <TextField
                  size="small"
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  placeholder="Add category"
                />
                <Button variant="contained" onClick={handleAddCategory}>
                  Add
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {preferences.preferred_categories.map((category) => (
                  <Chip
                    key={category}
                    label={category}
                    onDelete={() => handleDeleteCategory(category)}
                  />
                ))}
              </Box>
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Price Range
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    type="number"
                    label="Min Price"
                    value={preferences.price_range[0]}
                    onChange={(e) => setPreferences(prev => ({
                      ...prev,
                      price_range: [Number(e.target.value), prev.price_range[1]]
                    }))}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    type="number"
                    label="Max Price"
                    value={preferences.price_range[1]}
                    onChange={(e) => setPreferences(prev => ({
                      ...prev,
                      price_range: [prev.price_range[0], Number(e.target.value)]
                    }))}
                    fullWidth
                  />
                </Grid>
              </Grid>
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Preferred Brands
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <TextField
                  size="small"
                  value={newBrand}
                  onChange={(e) => setNewBrand(e.target.value)}
                  placeholder="Add brand"
                />
                <Button variant="contained" onClick={handleAddBrand}>
                  Add
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {preferences.preferred_brands.map((brand) => (
                  <Chip
                    key={brand}
                    label={brand}
                    onDelete={() => handleDeleteBrand(brand)}
                  />
                ))}
              </Box>
            </Box>

            <Button
              variant="contained"
              color="primary"
              onClick={handleSavePreferences}
              disabled={loading}
              fullWidth
            >
              {loading ? 'Saving...' : 'Save Preferences'}
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Shopping History
            </Typography>
            <Typography color="text.secondary">
              Your shopping history and analytics will appear here.
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Profile