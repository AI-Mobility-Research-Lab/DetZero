"""Property-based tests for Class Mapper component.

Feature: nuscenes-8k-to-detzero-conversion
"""

import numpy as np
from hypothesis import given, settings, strategies as st

# Import the component under test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from class_mapper import ClassMapper


# Custom strategies for generating test data
@st.composite
def nuscenes_class_name(draw):
    """Generate a nuScenes class name (both mapped and unmapped)."""
    all_classes = [
        # Mapped classes
        'car', 'truck', 'bus', 'trailer', 'construction_vehicle',
        'pedestrian', 'bicycle', 'motorcycle',
        # Unmapped classes
        'barrier', 'traffic_cone', 'animal'
    ]
    return draw(st.sampled_from(all_classes))


@st.composite
def mapped_nuscenes_class_name(draw):
    """Generate only mappable nuScenes class names."""
    mapped_classes = [
        'car', 'truck', 'bus', 'trailer', 'construction_vehicle',
        'pedestrian', 'bicycle', 'motorcycle'
    ]
    return draw(st.sampled_from(mapped_classes))


@st.composite
def annotation_data(draw, n_objects=None):
    """Generate annotation data with class names and other fields."""
    if n_objects is None:
        n_objects = draw(st.integers(min_value=0, max_value=50))
    
    # Generate class names (mix of mapped and unmapped)
    names = np.array([draw(nuscenes_class_name()) for _ in range(n_objects)])
    
    # Generate other annotation fields
    annotations = {
        'name': names,
        'dimensions': np.random.randn(n_objects, 3).astype(np.float32),
        'location': np.random.randn(n_objects, 3).astype(np.float32),
        'heading_angles': np.random.randn(n_objects).astype(np.float32),
        'velocity': np.random.randn(n_objects, 2).astype(np.float32),
        'obj_ids': np.array([f'track_{i}' for i in range(n_objects)]),
        'num_points_in_gt': np.random.randint(0, 1000, size=n_objects).astype(np.int32),
        'gt_boxes_lidar': np.random.randn(n_objects, 9).astype(np.float32),
    }
    
    return annotations


@st.composite
def mapped_annotation_data(draw, n_objects=None):
    """Generate annotation data with only mappable class names."""
    if n_objects is None:
        n_objects = draw(st.integers(min_value=1, max_value=50))
    
    # Generate only mapped class names
    names = np.array([draw(mapped_nuscenes_class_name()) for _ in range(n_objects)])
    
    # Generate other annotation fields
    annotations = {
        'name': names,
        'dimensions': np.random.randn(n_objects, 3).astype(np.float32),
        'location': np.random.randn(n_objects, 3).astype(np.float32),
        'heading_angles': np.random.randn(n_objects).astype(np.float32),
        'velocity': np.random.randn(n_objects, 2).astype(np.float32),
        'obj_ids': np.array([f'track_{i}' for i in range(n_objects)]),
        'num_points_in_gt': np.random.randint(0, 1000, size=n_objects).astype(np.int32),
        'gt_boxes_lidar': np.random.randn(n_objects, 9).astype(np.float32),
    }
    
    return annotations


class TestClassMapperProperties:
    """Property-based tests for ClassMapper."""
    
    @settings(max_examples=100)
    @given(annotations=mapped_annotation_data(n_objects=None))
    def test_property_7_class_label_preservation_after_mapping(self, annotations):
        """Property 7: Class Label Preservation After Mapping
        
        For any object in the source dataset with a mappable class, the converted 
        output SHALL contain the correctly mapped Waymo class name.
        
        **Validates: Requirements 3.2**
        
        Feature: nuscenes-8k-to-detzero-conversion, Property 7: Class label preservation after mapping
        """
        # Initialize class mapper
        mapper = ClassMapper()
        
        # Get original class names
        original_names = annotations['name'].copy()
        
        # Filter annotations (this also maps class names)
        filtered = mapper.filter_annotations(original_names, annotations)
        
        # Property: All objects with mappable classes should be preserved
        assert len(filtered['name']) == len(original_names), \
            f"Expected {len(original_names)} objects, got {len(filtered['name'])}"
        
        # Property: Each class should be correctly mapped
        for i, (original_name, mapped_name) in enumerate(zip(original_names, filtered['name'])):
            expected_waymo_class = mapper.map_class(original_name)
            assert expected_waymo_class is not None, \
                f"Object {i}: class '{original_name}' should be mappable"
            assert mapped_name == expected_waymo_class, \
                f"Object {i}: class '{original_name}' should map to '{expected_waymo_class}', got '{mapped_name}'"
        
        # Property: Mapping should be deterministic
        # Map the same data again and verify we get the same result
        mapper2 = ClassMapper()
        filtered2 = mapper2.filter_annotations(original_names, annotations)
        np.testing.assert_array_equal(filtered['name'], filtered2['name'],
                                     "Class mapping should be deterministic")
    
    @settings(max_examples=100)
    @given(annotations=annotation_data(n_objects=None))
    def test_class_mapping_with_mixed_classes(self, annotations):
        """Property 7: Class Label Preservation (with unmapped classes)
        
        Verify that only mappable classes are preserved and correctly mapped,
        while unmapped classes are filtered out.
        
        **Validates: Requirements 3.2**
        
        Feature: nuscenes-8k-to-detzero-conversion, Property 7: Class label preservation after mapping
        """
        # Initialize class mapper
        mapper = ClassMapper()
        
        # Get original class names
        original_names = annotations['name'].copy()
        
        # Count how many are mappable
        mappable_count = sum(1 for name in original_names if mapper.map_class(name) is not None)
        
        # Filter annotations
        filtered = mapper.filter_annotations(original_names, annotations)
        
        # Property: Only mappable classes should remain
        assert len(filtered['name']) == mappable_count, \
            f"Expected {mappable_count} mappable objects, got {len(filtered['name'])}"
        
        # Property: All remaining classes should be valid Waymo classes
        valid_waymo_classes = {'Vehicle', 'Pedestrian', 'Cyclist'}
        for mapped_name in filtered['name']:
            assert mapped_name in valid_waymo_classes, \
                f"Mapped class '{mapped_name}' is not a valid Waymo class"
        
        # Property: Each mapped class should correspond to correct original class
        original_mappable = [name for name in original_names if mapper.map_class(name) is not None]
        for i, (original_name, mapped_name) in enumerate(zip(original_mappable, filtered['name'])):
            expected = mapper.map_class(original_name)
            assert mapped_name == expected, \
                f"Object {i}: '{original_name}' should map to '{expected}', got '{mapped_name}'"
    
    @settings(max_examples=100)
    @given(class_name=mapped_nuscenes_class_name())
    def test_class_mapping_determinism(self, class_name):
        """Property 7: Class Mapping Determinism
        
        Verify that class mapping is deterministic - the same input always
        produces the same output.
        
        **Validates: Requirements 3.2**
        
        Feature: nuscenes-8k-to-detzero-conversion, Property 7: Class label preservation after mapping
        """
        # Create multiple mappers
        mapper1 = ClassMapper()
        mapper2 = ClassMapper()
        mapper3 = ClassMapper()
        
        # Map the same class multiple times
        result1 = mapper1.map_class(class_name)
        result2 = mapper2.map_class(class_name)
        result3 = mapper3.map_class(class_name)
        
        # Property: All results should be identical
        assert result1 == result2 == result3, \
            f"Class mapping not deterministic: got {result1}, {result2}, {result3}"
        
        # Property: Result should be a valid Waymo class
        valid_waymo_classes = {'Vehicle', 'Pedestrian', 'Cyclist'}
        assert result1 in valid_waymo_classes, \
            f"Mapped class '{result1}' is not a valid Waymo class"
    
    @settings(max_examples=100)
    @given(annotations=mapped_annotation_data(n_objects=None))
    def test_annotation_field_preservation(self, annotations):
        """Property 7: Annotation Field Preservation During Mapping
        
        Verify that all annotation fields (not just class names) are preserved
        correctly when filtering and mapping.
        
        **Validates: Requirements 3.2**
        
        Feature: nuscenes-8k-to-detzero-conversion, Property 7: Class label preservation after mapping
        """
        # Initialize class mapper
        mapper = ClassMapper()
        
        # Get original data
        original_names = annotations['name'].copy()
        original_dimensions = annotations['dimensions'].copy()
        original_locations = annotations['location'].copy()
        
        # Filter annotations
        filtered = mapper.filter_annotations(original_names, annotations)
        
        # Property: All annotation fields should be present
        expected_fields = {'name', 'dimensions', 'location', 'heading_angles', 
                          'velocity', 'obj_ids', 'num_points_in_gt', 'gt_boxes_lidar'}
        assert set(filtered.keys()) == expected_fields, \
            f"Missing or extra fields in filtered annotations"
        
        # Property: Non-name fields should preserve their values (since all classes are mappable)
        assert len(filtered['dimensions']) == len(original_dimensions), \
            "Dimensions array length mismatch"
        np.testing.assert_array_almost_equal(filtered['dimensions'], original_dimensions,
                                            err_msg="Dimensions not preserved")
        
        assert len(filtered['location']) == len(original_locations), \
            "Location array length mismatch"
        np.testing.assert_array_almost_equal(filtered['location'], original_locations,
                                            err_msg="Locations not preserved")
        
        # Property: Array shapes should be consistent
        n_objects = len(filtered['name'])
        assert filtered['dimensions'].shape == (n_objects, 3), \
            f"Dimensions shape should be ({n_objects}, 3)"
        assert filtered['location'].shape == (n_objects, 3), \
            f"Location shape should be ({n_objects}, 3)"
        assert filtered['velocity'].shape == (n_objects, 2), \
            f"Velocity shape should be ({n_objects}, 2)"
        assert filtered['gt_boxes_lidar'].shape == (n_objects, 9), \
            f"gt_boxes_lidar shape should be ({n_objects}, 9)"
    
    @settings(max_examples=100)
    @given(
        car_count=st.integers(min_value=0, max_value=20),
        pedestrian_count=st.integers(min_value=0, max_value=20),
        bicycle_count=st.integers(min_value=0, max_value=20)
    )
    def test_specific_class_mappings(self, car_count, pedestrian_count, bicycle_count):
        """Property 7: Specific Class Mapping Correctness
        
        Verify that specific nuScenes classes map to the correct Waymo classes:
        - car, truck, bus, trailer, construction_vehicle -> Vehicle
        - pedestrian -> Pedestrian
        - bicycle, motorcycle -> Cyclist
        
        **Validates: Requirements 3.2**
        
        Feature: nuscenes-8k-to-detzero-conversion, Property 7: Class label preservation after mapping
        """
        # Skip if all counts are zero
        if car_count == 0 and pedestrian_count == 0 and bicycle_count == 0:
            return
        
        # Initialize class mapper
        mapper = ClassMapper()
        
        # Create class names array
        names = []
        names.extend(['car'] * car_count)
        names.extend(['pedestrian'] * pedestrian_count)
        names.extend(['bicycle'] * bicycle_count)
        names = np.array(names)
        
        # Create dummy annotations
        n_objects = len(names)
        annotations = {
            'name': names,
            'dimensions': np.random.randn(n_objects, 3).astype(np.float32),
            'location': np.random.randn(n_objects, 3).astype(np.float32),
            'heading_angles': np.random.randn(n_objects).astype(np.float32),
            'velocity': np.random.randn(n_objects, 2).astype(np.float32),
            'obj_ids': np.array([f'track_{i}' for i in range(n_objects)]),
            'num_points_in_gt': np.random.randint(0, 1000, size=n_objects).astype(np.int32),
            'gt_boxes_lidar': np.random.randn(n_objects, 9).astype(np.float32),
        }
        
        # Filter annotations
        filtered = mapper.filter_annotations(names, annotations)
        
        # Property: All objects should be preserved (all are mappable)
        assert len(filtered['name']) == n_objects, \
            f"Expected {n_objects} objects, got {len(filtered['name'])}"
        
        # Property: Count each Waymo class
        vehicle_count = np.sum(filtered['name'] == 'Vehicle')
        pedestrian_mapped_count = np.sum(filtered['name'] == 'Pedestrian')
        cyclist_count = np.sum(filtered['name'] == 'Cyclist')
        
        assert vehicle_count == car_count, \
            f"Expected {car_count} Vehicles, got {vehicle_count}"
        assert pedestrian_mapped_count == pedestrian_count, \
            f"Expected {pedestrian_count} Pedestrians, got {pedestrian_mapped_count}"
        assert cyclist_count == bicycle_count, \
            f"Expected {bicycle_count} Cyclists, got {cyclist_count}"


    @settings(max_examples=100)
    @given(annotations=annotation_data(n_objects=None))
    def test_property_11_unmapped_class_filtering(self, annotations):
        """Property 11: Unmapped Class Filtering
        
        For any object with a nuScenes class that has no Waymo mapping, that object 
        SHALL NOT appear in the converted output annotations.
        
        **Validates: Requirements 4.5**
        
        Feature: nuscenes-8k-to-detzero-conversion, Property 11: Unmapped class filtering
        """
        # Initialize class mapper
        mapper = ClassMapper()
        
        # Get original class names
        original_names = annotations['name'].copy()
        
        # Identify which classes are unmapped
        unmapped_classes = {'barrier', 'traffic_cone', 'animal'}
        unmapped_mask = np.array([name in unmapped_classes for name in original_names], dtype=bool)
        mapped_mask = np.logical_not(unmapped_mask)
        
        # Count unmapped and mapped objects
        unmapped_count = np.sum(unmapped_mask)
        mapped_count = np.sum(mapped_mask)
        
        # Filter annotations
        filtered = mapper.filter_annotations(original_names, annotations)
        
        # Property: No unmapped classes should appear in output
        for name in filtered['name']:
            assert name not in unmapped_classes, \
                f"Unmapped class '{name}' should not appear in filtered output"
        
        # Property: Only mapped classes should remain
        assert len(filtered['name']) == mapped_count, \
            f"Expected {mapped_count} mapped objects, got {len(filtered['name'])}"
        
        # Property: All filtered classes should be valid Waymo classes
        valid_waymo_classes = {'Vehicle', 'Pedestrian', 'Cyclist'}
        for mapped_name in filtered['name']:
            assert mapped_name in valid_waymo_classes, \
                f"Filtered class '{mapped_name}' is not a valid Waymo class"
        
        # Property: If all objects are unmapped, output should be empty
        if unmapped_count == len(original_names) and len(original_names) > 0:
            assert len(filtered['name']) == 0, \
                "When all objects are unmapped, output should be empty"
            # Verify all annotation arrays are empty
            for key in ['dimensions', 'location', 'heading_angles', 'velocity', 
                       'obj_ids', 'num_points_in_gt', 'gt_boxes_lidar']:
                assert len(filtered[key]) == 0, \
                    f"Field '{key}' should be empty when all objects are unmapped"
        
        # Property: If all objects are mapped, all should be preserved
        if mapped_count == len(original_names) and len(original_names) > 0:
            assert len(filtered['name']) == len(original_names), \
                "When all objects are mapped, all should be preserved"
        
        # Property: Filtered objects should maintain relative ordering
        # Extract the mapped objects from original in order
        if mapped_count > 0:
            original_mapped = original_names[mapped_mask]
            expected_waymo_classes = np.array([mapper.map_class(name) for name in original_mapped])
            np.testing.assert_array_equal(filtered['name'], expected_waymo_classes,
                                         "Filtered objects should maintain relative ordering")
        
        # Property: All annotation fields should have consistent lengths
        n_filtered = len(filtered['name'])
        assert filtered['dimensions'].shape[0] == n_filtered, \
            "Dimensions array length should match filtered object count"
        assert filtered['location'].shape[0] == n_filtered, \
            "Location array length should match filtered object count"
        assert filtered['heading_angles'].shape[0] == n_filtered, \
            "Heading angles array length should match filtered object count"
        assert filtered['velocity'].shape[0] == n_filtered, \
            "Velocity array length should match filtered object count"
        assert len(filtered['obj_ids']) == n_filtered, \
            "Object IDs array length should match filtered object count"
        assert filtered['num_points_in_gt'].shape[0] == n_filtered, \
            "Num points array length should match filtered object count"
        assert filtered['gt_boxes_lidar'].shape[0] == n_filtered, \
            "GT boxes array length should match filtered object count"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
