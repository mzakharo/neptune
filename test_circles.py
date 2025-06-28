import cv2
import numpy as np
import matplotlib.pyplot as plt

def test_hough_circles(img, param1_range, param2_range, min_radius_range, max_radius_range, min_dist_factor_range):
    """
    Test different HoughCircles parameters to find optimal settings for detecting exactly 2 circles.
    """
    results = []
    gray = img
    rows = gray.shape[0]
    
    for param1 in param1_range:
        for param2 in param2_range:
            for min_radius in min_radius_range:
                for max_radius in max_radius_range:
                    for min_dist_factor in min_dist_factor_range:
                        min_dist = rows / min_dist_factor
                        
                        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, min_dist,
                                                    param1=param1, param2=param2,
                                                    minRadius=min_radius, maxRadius=max_radius)
                        
                        num_circles = 0 if circles is None else len(circles[0])
                        
                        results.append({
                            'param1': param1,
                            'param2': param2,
                            'min_radius': min_radius,
                            'max_radius': max_radius,
                            'min_dist_factor': min_dist_factor,
                            'min_dist': min_dist,
                            'num_circles': num_circles,
                            'circles': circles
                        })
    
    return results

def find_best_params_for_2_circles(results):
    """
    Find parameter combinations that detect exactly 2 circles.
    """
    two_circle_results = [r for r in results if r['num_circles'] == 2]
    return two_circle_results

def visualize_circles(img, circles, title="Detected Circles"):
    """
    Visualize detected circles on the image.
    """
    output = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    
    plt.figure(figsize=(12, 8))
    plt.imshow(output)
    plt.title(f"{title} - Found {len(circles[0]) if circles is not None else 0} circles")
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    # Load and prepare image
    img_file = 'data/ref_error.jpeg'
    img_orig = cv2.imread(img_file)
    img_orig = cv2.rotate(img_orig, cv2.ROTATE_180)
    img = cv2.cvtColor(img_orig, cv2.COLOR_BGR2GRAY)
    
    print(f"Image shape: {img.shape}")
    
    # Define parameter ranges to test
    param1_range = [30, 40, 50, 60, 70]
    param2_range = [15, 20, 25, 30, 35]
    min_radius_range = [5, 7, 9, 11]
    max_radius_range = [11, 13, 15, 17]
    min_dist_factor_range = [8, 12, 16, 20, 24]
    
    print("Testing HoughCircles parameters...")
    results = test_hough_circles(img, param1_range, param2_range, min_radius_range, max_radius_range, min_dist_factor_range)
    
    # Find combinations that detect exactly 2 circles
    two_circle_results = find_best_params_for_2_circles(results)
    
    print(f"\nFound {len(two_circle_results)} parameter combinations that detect exactly 2 circles:")
    
    for i, result in enumerate(two_circle_results[:10]):  # Show first 10 results
        print(f"\nOption {i+1}:")
        print(f"  param1={result['param1']}, param2={result['param2']}")
        print(f"  minRadius={result['min_radius']}, maxRadius={result['max_radius']}")
        print(f"  minDist={result['min_dist']:.1f} (rows/{result['min_dist_factor']})")
        
        # Show circle positions
        if result['circles'] is not None:
            circles = np.round(result['circles'][0, :]).astype("int")
            circles_sorted = sorted(list(circles), key=lambda x: x[0], reverse=True)
            for j, (x, y, r) in enumerate(circles_sorted):
                print(f"    Circle {j+1}: center=({x}, {y}), radius={r}")
    
    # Visualize the best result
    if two_circle_results:
        best_result = two_circle_results[0]
        print(f"\nVisualizing best result:")
        visualize_circles(img, best_result['circles'], "Best Parameters for 2 Circles")
