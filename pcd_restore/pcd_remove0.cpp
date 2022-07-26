#include <iostream>
#include <string>

#include <pcl/point_types.h>
#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>
//#include <pcl/registration/icp.h>
//#include <json/json.h>
//#include <Eigen/Dense>
#include <math.h>

using namespace Eigen;


struct PointXYZIT {
    float x;
    float y;
    float z;
    float intensity;
    double timestamp;
    std::uint16_t ring;                      ///< laser ring number
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW // make sure our new allocators are aligned
} EIGEN_ALIGN16;


POINT_CLOUD_REGISTER_POINT_STRUCT(PointXYZIT,
                                  (float, x, x)(float, y, y)(float, z, z)
                                  (float, intensity, intensity)(double, timestamp, timestamp)(std::uint16_t, ring, ring))



typedef PointXYZIT PointT;
typedef pcl::PointCloud<PointT> PointCloudT;


// pcd_restore  pcdfile timestamp dx dy dz droll dpitch dyaw order
// note deltas are in lidar coordinate system at specified timestamp
int main (int argc, char* argv[])
{

  if (argc !=3 )
  {
    std::cerr << "pcd_remove0 pcdfile outputfile" << std::endl;
    return 0;
  }

  PointCloudT::Ptr cloud (new PointCloudT);
  PointCloudT::Ptr cloud_out (new PointCloudT);  
  //load pcd
  if (pcl::io::loadPCDFile<PointXYZIT> (argv[1], *cloud) == -1) //* load the file
  {
    PCL_ERROR ("Couldn't read the .pcd file \n");
    return (-1);
  }
  




  for (pcl::PointCloud<PointT>::iterator p = cloud->points.begin(); p != cloud->points.end(); ++p)
  {
    if (p->x !=0 || p->y != 0 || p->z !=0) //filter nan data
    {
      cloud_out->points.push_back(*p); 
    }    
  }

  
  pcl::io::savePCDFileBinary(argv[2], *cloud_out);

}
