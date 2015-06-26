/*=========================================================================

  Library   : Image Registration Toolkit (IRTK)
  Module    : $Id: irtkLaplacianSmoothingMissingData.h 998 2013-10-15 15:24:16Z mm3 $
  Copyright : Imperial College, Department of Computing
              Visual Information Processing (VIP), 2011 onwards
  Date      : $Date: 2013-10-15 16:24:16 +0100 (Tue, 15 Oct 2013) $
  Version   : $Revision: 998 $
  Changes   : $Author: mm3 $

=========================================================================*/

#ifndef _irtkLaplacianSmoothingMissingData_H

#define _irtkLaplacianSmoothingMissingData_H

#include <irtkImage.h>
#include <irtkTransformation.h>
#include <irtkGaussianBlurring.h>
#include <irtkGaussianBlurringWithPadding.h>
#include <irtkResampling.h>
#include <irtkResamplingWithPadding.h>



class irtkLaplacianSmoothingMissingData : public irtkObject
{

protected:

  irtkRealImage _image;
  irtkRealImage _fieldmap;
  irtkRealImage _mask;
  irtkRealImage _image_mask;
  irtkRealImage _m;
  irtkRealImage _target;
  bool _have_target;
  int _directions[13][3]; 

  vector<double> _factor;//(13,0);

  
  void InitializeFactors();
  
  void Blur(irtkRealImage& image, double sigma, irtkRealImage& mask, double padding);
  void Resample(irtkRealImage& image, double step, double padding);
  void SetPaddingToZero(irtkRealImage& image, double padding);
  void EnlargeImage(irtkRealImage &image);
  void ReduceImage(irtkRealImage &image);
  
  void CalculateBoundary(irtkRealImage& m);
  void CalculateBoundaryWeights(irtkRealImage& w, irtkRealImage m);
  double LaplacianImage(irtkRealImage image, irtkRealImage m, irtkRealImage& laplacian);
  double LaplacianBoundary(irtkRealImage image, irtkRealImage m, irtkRealImage& laplacian);
  void UpdateFieldmap(irtkRealImage& fieldmap, irtkRealImage image, irtkRealImage multipliers, 
		    irtkRealImage mask, irtkRealImage image_mask, irtkRealImage weights, double alpha);
  
  void Smooth(irtkRealImage& im, irtkRealImage m, irtkRealImage imask);
  void UpsampleFieldmap(irtkRealImage& target, irtkRealImage mask, irtkRealImage newmask);

  
public:
  
  irtkLaplacianSmoothingMissingData();
  
  void SetInput(irtkRealImage image);
  void SetMask(irtkRealImage mask);
  void SetInputMask(irtkRealImage mask);
  
  irtkRealImage Run();
  irtkRealImage Run3levels();

};

inline void irtkLaplacianSmoothingMissingData::SetInput(irtkRealImage image)
{
  _image = image;
  _mask = _image;
  _mask=1;
}

inline void irtkLaplacianSmoothingMissingData::SetMask(irtkRealImage mask)
{
  _mask = mask;
}

inline void irtkLaplacianSmoothingMissingData::SetInputMask(irtkRealImage mask)
{
  _image_mask = mask;
}

#endif