
#include<map>
#include<memory>
#include"AlgParamBase.h"
#ifdef ALGINSPECT_EXPORT
#define DLL_EXPORT __declspec(dllexport)
#else
#define DLL_EXPORT __declspec(dllimport)
#endif
#pragma execution_character_set("utf-8")
//API for AlgParam  By CH20190118  BOZHON

extern "C" DLL_EXPORT CreateAlgParamFunction GetAlgParamRegistFunctionPt();//检测参数对象注册指针
extern "C" DLL_EXPORT char* GetAlgParamRegistAlgParamName();//检测类名中文接口
extern "C" DLL_EXPORT char* GetAlgParamRegistAlgName();//检测类名中文接口
