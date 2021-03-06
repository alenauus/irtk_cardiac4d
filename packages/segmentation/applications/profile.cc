/*=========================================================================

  Library   : Image Registration Toolkit (IRTK)
  Module    : $Id: reconstructionb0.cc 1000 2013-10-18 16:49:08Z mm3 $
  Copyright : Imperial College, Department of Computing
              Visual Information Processing (VIP), 2011 onwards
  Date      : $Date: 2013-10-18 17:49:08 +0100 (Fri, 18 Oct 2013) $
  Version   : $Revision: 1000 $
  Changes   : $Author: mm3 $

=========================================================================*/

#include <irtkImage.h>
#include <irtkTransformation.h>
#include <irtkReconstruction.h>
#include <irtkReconstructionb0.h>
#include <vector>
#include <string>
using namespace std;

//Application to perform reconstruction of volumetric MRI from thick slices.

void usage()
{
  cerr << "Usage: ssd [image] <-file>\n" << endl;
  cerr << endl;
  exit(1);
}

int main(int argc, char **argv)
{
  
  int ok;
  char buffer[256];
  irtkRealImage image, image2, m;  
  irtkRealImage *mask=NULL;
  char *file_name=NULL;
  char *method=NULL;
  double padding=0;
  bool minus = false;
    
  //if not enough arguments print help
  if (argc < 2)
    usage();
  
  image.Read(argv[1]);  
  argc--;
  argv++;
  
  //image2.Read(argv[1]);  
  //argc--;
  //argv++;
  
  
  // Parse options.
  while (argc > 1){
    ok = false;
    

    //Read binary mask for final volume
    if ((ok == false) && (strcmp(argv[1], "-mask") == 0)){
      argc--;
      argv++;
      mask= new irtkRealImage(argv[1]);
      ok = true;
      argc--;
      argv++;
    }
    
    if ((ok == false) && (strcmp(argv[1], "-file") == 0)){
      argc--;
      argv++;

      file_name = argv[1];

      argc--;
      argv++;
      ok = true;
    }

    if ((ok == false) && (strcmp(argv[1], "-method") == 0)){
      argc--;
      argv++;

      method = argv[1];

      argc--;
      argv++;
      ok = true;
    }

    if ((ok == false) && (strcmp(argv[1], "-padding") == 0)){
      argc--;
      argv++;

      padding = atof(argv[1]);

      argc--;
      argv++;
      ok = true;
    }

    if ((ok == false) && (strcmp(argv[1], "-minus") == 0)){
      argc--;
      argv++;
      minus=true;
      cout<< "Sign of phase endoding direction is minus."<<endl;
      cout.flush();
      ok = true;
    }
    
    if (ok == false){
      cerr << "Can not parse argument " << argv[1] << endl;
      usage();
    }
  }
  
  
  irtkImageAttributes attr = image.GetImageAttributes();
  for (int t=0;t<image.GetT();t++)
  {
    irtkRealImage stack = image.GetRegion(0, 0, 0,t, attr._x, attr._y, attr._z,t+1);
    sprintf(buffer,"stack%i.nii.gz",t);
    stack.Write(buffer);
  }
  
  
  if (file_name !=NULL)
  {
    ofstream fileOut(file_name, ofstream::out | ofstream::app);

    if(!fileOut)
    {
      cerr << "Can't open file " << file_name << endl;
      exit(1);
    }
    else
      cout<<"file open"<<endl;
    fileOut.precision(3); 
    
    for(int i=0;i<image.GetT();i++)
    {
      fileOut<<i<<" ";
      cout<<i<<" ";
    }
    //exit(1);
 
  double average;
  int num;
  for (int t=0;t<image.GetT();t++)
  {
    average =0;
    num=0;
    for (int i=0;i<image.GetX();i++)
      for (int j=0;j<image.GetY();j++)
        for (int k=0;k<image.GetZ();k++)
	{
	  average+=image(i,j,k,t);
	  num++;
	}
    average/=num;
    
    if (file_name !=NULL)
      fileOut<<t<<", "<<average<<endl;
    else
      cout<<t<<" "<<average<<endl;
    
  }	 
  } 
 
}  
