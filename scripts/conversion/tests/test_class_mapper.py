"""Unit tests for Class Mapper component.

Tests specific class mappings, unmapped class handling, and annotation filtering.
"""

import numpy as np
import pytest

# Import the component under test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from class_mapper import ClassMapper


class TestClassMapperSpecificMappings:
    """Test each specific class mapping as defined in requirements."""
    
    def test_car_maps_to_vehicle(self):
        """Requirement 4.1: car class SHALL map to Vehicle."""
        mapper = ClassMapper()
        assert mapper.map_class('car') == 'Vehicle'
    
    def test_truck_maps_to_vehicle(self):
        """Requirement 4.2: truck class SHALL map to Vehicle."""
        mapper = ClassMapper()
        assert mapper.map_class('truck') == 'Vehicle'
    
    def test_pedestrian_maps_to_pedestrian(self):
        """Requirement 4.3: pedestrian class SHALL map to Pedestrian."""
        mapper = ClassMapper()
        assert mapper.map_class('pedestrian') == 'Pedestrian'
    
    def test_bicycle_maps_to_cyclist(self):
        """Requirement 4.4: bicycle class SHALL map to Cyclist."""
        mapper = ClassMapper()
        assert mapper.map_class('bicycle') == 'Cyclist'
    
    def test_bus_maps_to_vehicle(self):
        """Additional mapping: bus class SHALL map to Vehicle."""
        mapper = ClassMapper()
        assert mapper.map_class('bus') == 'Vehicle'
    
    def test_trailer_maps_to_vehicle(self):
        """Additional mapping: trailer class SHALL map to Vehicle."""
        mapper = ClassMapper()
        assert mapper.map_class('trailer') == 'Vehicle'
    
    def test_construction_vehicle_maps_to_vehicle(self):
        """Additional mapping: construction_vehicle class SHALL map to Vehicle."""
        mapper = ClassMapper()
        assert mapper.map_class('construction_vehicle') == 'Vehicle'
    
    def test_motorcycle_maps_to_cyclist(self):
        """Additional mapping: motorcycle class SHALL map to Cyclist."""
        mapper = ClassMapper()
        assert mapper.map_class('motorcycle') == 'Cyclist'


class TestUnmappedClassHandling:
    """Test handling of classes with no Waymo equivalent."""
    
    def test_barrier_has_no_mapping(self):
        """Requirement 4.5: barrier class has no Waymo equivalent."""
        mapper = ClassMapper()
        assert mapper.map_class('barrier') is None
    
    def test_traffic_cone_has_no_mapping(self):
        """Requirement 4.5: traffic_cone class has no Waymo equivalent."""
        mapper = ClassMapper()
        assert mapper.map_class('traffic_cone') is None
    
    def test_animal_has_no_mapping(self):
        """Requirement 4.5: animal class has no Waymo equivalent."""
        mapper = ClassMapper()
        assert mapper.map_class('animal') is None
    
    def test_unknown_class_has_no_mapping(self):
        """Requirement 4.5: unknown classes have no Waymo equivalent."""
        mapper = ClassMapper()
        assert mapper.map_class('unknown_class') is None
        assert mapper.map_class('') is None
    
    def test_unmapped_class_tracking(self):
        """Verify that unmapped classes are tracked for logging."""
        mapper = ClassMapper()
        
        # Map some unmapped classes
        mapper.map_class('barrier')
        mapper.map_class('barrier')
        mapper.map_class('traffic_cone')
        
        # Verify counts are tracked
        assert mapper.unmapped_counts['barrier'] == 2
        assert mapper.unmapped_counts['traffic_cone'] == 1


class TestAnnotationFiltering:
    """Test annotation filtering with mapped and unmapped classes."""
    
    def test_filter_all_mapped_classes(self):
        """Test filtering when all classes are mapped."""
        mapper = ClassMapper()
        
        # Create annotations with only mapped classes
        names = np.array(['car', 'pedestrian', 'bicycle'])
        annotations = {
            'name': names,
            'dimensions': np.array([[4.0, 2.0, 1.5], [0.6, 0.6, 1.7], [1.8, 0.6, 1.2]]),
            'location': np.array([[10.0, 5.0, 0.0], [15.0, 3.0, 0.0], [8.0, -2.0, 0.0]]),
            'heading_angles': np.array([0.5, 1.2, -0.3]),
            'velocity': np.array([[2.0, 0.5], [1.0, 0.2], [3.0, -0.5]]),
            'obj_ids': np.array(['track_1', 'track_2', 'track_3']),
            'num_points_in_gt': np.array([100, 50, 75]),
            'gt_boxes_lidar': np.random.randn(3, 9).astype(np.float32),
        }
        
        # Filter annotations
        filtered = mapper.filter_annotations(names, annotations)
        
        # All objects should be preserved
        assert len(filtered['name']) == 3
        assert filtered['name'][0] == 'Vehicle'
        assert filtered['name'][1] == 'Pedestrian'
        assert filtered['name'][2] == 'Cyclist'
        
        # Other fields should be preserved
        assert len(filtered['dimensions']) == 3
        assert len(filtered['location']) == 3
        assert len(filtered['heading_angles']) == 3
        assert len(filtered['velocity']) == 3
        assert len(filtered['obj_ids']) == 3
        assert len(filtered['num_points_in_gt']) == 3
        assert len(filtered['gt_boxes_lidar']) == 3
    
    def test_filter_all_unmapped_classes(self):
        """Test filtering when all classes are unmapped."""
        mapper = ClassMapper()
        
        # Create annotations with only unmapped classes
        names = np.array(['barrier', 'traffic_cone', 'animal'])
        annotations = {
            'name': names,
            'dimensions': np.array([[4.0, 2.0, 1.5], [0.6, 0.6, 1.7], [1.8, 0.6, 1.2]]),
            'location': np.array([[10.0, 5.0, 0.0], [15.0, 3.0, 0.0], [8.0, -2.0, 0.0]]),
            'heading_angles': np.array([0.5, 1.2, -0.3]),
            'velocity': np.array([[2.0, 0.5], [1.0, 0.2], [3.0, -0.5]]),
            'obj_ids': np.array(['track_1', 'track_2', 'track_3']),
            'num_points_in_gt': np.array([100, 50, 75]),
            'gt_boxes_lidar': np.random.randn(3, 9).astype(np.float32),
        }
        
        # Filter annotations
        filtered = mapper.filter_annotations(names, annotations)
        
        # All objects should be filtered out
        assert len(filtered['name']) == 0
        assert len(filtered['dimensions']) == 0
        assert len(filtered['location']) == 0
        assert len(filtered['heading_angles']) == 0
        assert len(filtered['velocity']) == 0
        assert len(filtered['obj_ids']) == 0
        assert len(filtered['num_points_in_gt']) == 0
        assert len(filtered['gt_boxes_lidar']) == 0
    
    def test_filter_mixed_classes(self):
        """Test filtering with mix of mapped and unmapped classes."""
        mapper = ClassMapper()
        
        # Create annotations with mixed classes
        names = np.array(['car', 'barrier', 'pedestrian', 'traffic_cone', 'bicycle'])
        annotations = {
            'name': names,
            'dimensions': np.array([[4.0, 2.0, 1.5], [1.0, 1.0, 1.0], [0.6, 0.6, 1.7], 
                                   [0.5, 0.5, 0.8], [1.8, 0.6, 1.2]]),
            'location': np.array([[10.0, 5.0, 0.0], [12.0, 6.0, 0.0], [15.0, 3.0, 0.0],
                                 [18.0, 4.0, 0.0], [8.0, -2.0, 0.0]]),
            'heading_angles': np.array([0.5, 0.0, 1.2, 0.0, -0.3]),
            'velocity': np.array([[2.0, 0.5], [0.0, 0.0], [1.0, 0.2], [0.0, 0.0], [3.0, -0.5]]),
            'obj_ids': np.array(['track_1', 'track_2', 'track_3', 'track_4', 'track_5']),
            'num_points_in_gt': np.array([100, 80, 50, 30, 75]),
            'gt_boxes_lidar': np.random.randn(5, 9).astype(np.float32),
        }
        
        # Filter annotations
        filtered = mapper.filter_annotations(names, annotations)
        
        # Only mapped classes should remain (car, pedestrian, bicycle)
        assert len(filtered['name']) == 3
        assert filtered['name'][0] == 'Vehicle'
        assert filtered['name'][1] == 'Pedestrian'
        assert filtered['name'][2] == 'Cyclist'
        
        # Verify correct objects were preserved (indices 0, 2, 4)
        np.testing.assert_array_almost_equal(
            filtered['dimensions'][0], 
            annotations['dimensions'][0]
        )
        np.testing.assert_array_almost_equal(
            filtered['dimensions'][1], 
            annotations['dimensions'][2]
        )
        np.testing.assert_array_almost_equal(
            filtered['dimensions'][2], 
            annotations['dimensions'][4]
        )
        
        assert filtered['obj_ids'][0] == 'track_1'
        assert filtered['obj_ids'][1] == 'track_3'
        assert filtered['obj_ids'][2] == 'track_5'
    
    def test_filter_preserves_array_ordering(self):
        """Requirement 4.5: Test that annotation filtering preserves array ordering."""
        mapper = ClassMapper()
        
        # Create annotations with specific ordering
        names = np.array(['car', 'truck', 'barrier', 'pedestrian', 'traffic_cone', 
                         'bicycle', 'motorcycle', 'animal', 'bus'])
        n_objects = len(names)
        
        # Create sequential data to verify ordering
        annotations = {
            'name': names,
            'dimensions': np.arange(n_objects * 3).reshape(n_objects, 3).astype(np.float32),
            'location': np.arange(n_objects * 3).reshape(n_objects, 3).astype(np.float32) + 100,
            'heading_angles': np.arange(n_objects).astype(np.float32),
            'velocity': np.arange(n_objects * 2).reshape(n_objects, 2).astype(np.float32),
            'obj_ids': np.array([f'track_{i}' for i in range(n_objects)]),
            'num_points_in_gt': np.arange(n_objects).astype(np.int32),
            'gt_boxes_lidar': np.arange(n_objects * 9).reshape(n_objects, 9).astype(np.float32),
        }
        
        # Filter annotations
        filtered = mapper.filter_annotations(names, annotations)
        
        # Expected mapped classes in order: car, truck, pedestrian, bicycle, motorcycle, bus
        # Indices: 0, 1, 3, 5, 6, 8
        expected_indices = [0, 1, 3, 5, 6, 8]
        assert len(filtered['name']) == len(expected_indices)
        
        # Verify ordering is preserved
        for i, orig_idx in enumerate(expected_indices):
            # Check dimensions ordering
            np.testing.assert_array_equal(
                filtered['dimensions'][i],
                annotations['dimensions'][orig_idx]
            )
            
            # Check location ordering
            np.testing.assert_array_equal(
                filtered['location'][i],
                annotations['location'][orig_idx]
            )
            
            # Check heading angles ordering
            assert filtered['heading_angles'][i] == annotations['heading_angles'][orig_idx]
            
            # Check velocity ordering
            np.testing.assert_array_equal(
                filtered['velocity'][i],
                annotations['velocity'][orig_idx]
            )
            
            # Check obj_ids ordering
            assert filtered['obj_ids'][i] == annotations['obj_ids'][orig_idx]
            
            # Check num_points ordering
            assert filtered['num_points_in_gt'][i] == annotations['num_points_in_gt'][orig_idx]
            
            # Check gt_boxes ordering
            np.testing.assert_array_equal(
                filtered['gt_boxes_lidar'][i],
                annotations['gt_boxes_lidar'][orig_idx]
            )
    
    def test_filter_empty_annotations(self):
        """Test filtering with empty annotations."""
        mapper = ClassMapper()
        
        # Create empty annotations
        names = np.array([])
        annotations = {
            'name': names,
            'dimensions': np.array([]).reshape(0, 3),
            'location': np.array([]).reshape(0, 3),
            'heading_angles': np.array([]),
            'velocity': np.array([]).reshape(0, 2),
            'obj_ids': np.array([]),
            'num_points_in_gt': np.array([]),
            'gt_boxes_lidar': np.array([]).reshape(0, 9),
        }
        
        # Filter annotations
        filtered = mapper.filter_annotations(names, annotations)
        
        # Should return empty arrays
        assert len(filtered['name']) == 0
        assert len(filtered['dimensions']) == 0
        assert len(filtered['location']) == 0
        assert len(filtered['heading_angles']) == 0
        assert len(filtered['velocity']) == 0
        assert len(filtered['obj_ids']) == 0
        assert len(filtered['num_points_in_gt']) == 0
        assert len(filtered['gt_boxes_lidar']) == 0
    
    def test_filter_single_mapped_object(self):
        """Test filtering with single mapped object."""
        mapper = ClassMapper()
        
        names = np.array(['car'])
        annotations = {
            'name': names,
            'dimensions': np.array([[4.0, 2.0, 1.5]]),
            'location': np.array([[10.0, 5.0, 0.0]]),
            'heading_angles': np.array([0.5]),
            'velocity': np.array([[2.0, 0.5]]),
            'obj_ids': np.array(['track_1']),
            'num_points_in_gt': np.array([100]),
            'gt_boxes_lidar': np.random.randn(1, 9).astype(np.float32),
        }
        
        filtered = mapper.filter_annotations(names, annotations)
        
        assert len(filtered['name']) == 1
        assert filtered['name'][0] == 'Vehicle'
    
    def test_filter_single_unmapped_object(self):
        """Test filtering with single unmapped object."""
        mapper = ClassMapper()
        
        names = np.array(['barrier'])
        annotations = {
            'name': names,
            'dimensions': np.array([[1.0, 1.0, 1.0]]),
            'location': np.array([[10.0, 5.0, 0.0]]),
            'heading_angles': np.array([0.0]),
            'velocity': np.array([[0.0, 0.0]]),
            'obj_ids': np.array(['track_1']),
            'num_points_in_gt': np.array([50]),
            'gt_boxes_lidar': np.random.randn(1, 9).astype(np.float32),
        }
        
        filtered = mapper.filter_annotations(names, annotations)
        
        assert len(filtered['name']) == 0


class TestClassMapperLogging:
    """Test logging functionality."""
    
    def test_log_unmapped_summary_with_unmapped_classes(self, caplog):
        """Test that unmapped class summary is logged."""
        import logging
        caplog.set_level(logging.WARNING)
        
        mapper = ClassMapper()
        
        # Map some unmapped classes
        mapper.map_class('barrier')
        mapper.map_class('barrier')
        mapper.map_class('traffic_cone')
        
        # Log summary
        mapper.log_unmapped_summary()
        
        # Verify warning was logged
        assert 'unmapped class types' in caplog.text
        assert 'barrier' in caplog.text
        assert 'traffic_cone' in caplog.text
    
    def test_log_unmapped_summary_with_no_unmapped_classes(self, caplog):
        """Test that success message is logged when all classes are mapped."""
        import logging
        caplog.set_level(logging.INFO)
        
        mapper = ClassMapper()
        
        # Map only mapped classes
        mapper.map_class('car')
        mapper.map_class('pedestrian')
        
        # Log summary
        mapper.log_unmapped_summary()
        
        # Verify info message was logged
        assert 'All classes successfully mapped' in caplog.text


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
