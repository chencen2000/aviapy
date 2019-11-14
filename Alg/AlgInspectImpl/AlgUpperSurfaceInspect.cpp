#include "AlgUpperSurfaceInspect.h"
#include"QtFileOperate.h"
using namespace HalconCpp;

#include <GdiPlus.h>
#include <shlwapi.h>
using namespace Gdiplus;
#pragma comment(lib, "Gdiplus.lib")
#pragma comment(lib, "shlwapi.lib")
ULONG_PTR gdiplusToken;
TCHAR configPath[MAX_PATH] = { 0 };

CAlgDarkDefectInspect::CAlgDarkDefectInspect()
{

}

HMODULE GetCurrentModuleHandle()
{
	HMODULE hMod = NULL;
	GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
		reinterpret_cast<LPCWSTR>(&GetCurrentModuleHandle),
		&hMod);
	return hMod;
}
//系统初始化
bool CAlgDarkDefectInspect::Init(const s_AlgInitParam & sAlgInitParam)
{
	GdiplusStartupInput gdiplusStartupInput;
	GdiplusStartup(&gdiplusToken, &gdiplusStartupInput, NULL);
	HMODULE hm = NULL;

	GetModuleFileName(GetCurrentModuleHandle(), configPath, MAX_PATH);
	PathRenameExtensionW(configPath, L".ini");
	if (PathFileExistsW(configPath)) {
		GetPrivateProfileStringW(L"ImagePath", L"FDpath", L"", configPath, MAX_PATH, configPath);
	}
	else {
		PathRemoveFileSpec(configPath);
	}
    return true;
}

//检测函数
bool  CAlgDarkDefectInspect::GCheck(const s_AlgCheckInputParam &sAlgCheckInputParam, s_AlgCheckOutputParam &sAlgCheckOutputResult, int nGroupId, const sInspParams* pAlgParam, std::map<std::string, stag_HRegionRuns> *ptMapResult)
{
	if (nullptr == pAlgParam)
	{
		CQtFileOperate::PrintfDebugLog("AlgProcess-GCheck-InspId:%d-Page:%d-ErrInfo:pAlgParam is Empty!", sAlgCheckInputParam.iInspId, sAlgCheckInputParam.iPageIndex);
		return false;//参数内存为空
	}
	/*
	if (!pAlgParam->bFlagUsingState)
	{
		CQtFileOperate::PrintfDebugLog("AlgProcess-GCheck-InspId:%d-Page:%d-WarInfo:bFlagUsingState is Closed!", sAlgCheckInputParam.iInspId, sAlgCheckInputParam.iPageIndex);
		return true;//未开启检测
	}
	*/
	if (sAlgCheckInputParam.vImageData.empty() || ((!sAlgCheckInputParam.bMergel) && nullptr == sAlgCheckInputParam.vImageData[0].pDATA) || (sAlgCheckInputParam.bMergel&&nullptr == sAlgCheckInputParam.vImageData[sAlgCheckInputParam.vImageData.size() - 1].pDATA))
	{
		CQtFileOperate::PrintfDebugLog("AlgProcess-GCheck-InspId:%d-Page:%d-ErrInfo:ImageDate is Empty!", sAlgCheckInputParam.iInspId, sAlgCheckInputParam.iPageIndex);
		return false;//图像数据异常
	}
	int nImageWidth = 0;
	int nImageHeight = 0;
	for (int i = 0; i < sAlgCheckInputParam.vImageData.size(); i++)
	{
		nImageWidth = sAlgCheckInputParam.vImageData[i].nWidth;
		nImageHeight = sAlgCheckInputParam.vImageData[i].nHeight; 
		if (sAlgCheckInputParam.vImageData[i].nChannel == 1)
		{
			Gdiplus::Bitmap bmp(nImageWidth, nImageHeight, sAlgCheckInputParam.vImageData[i].nPixWidth, PixelFormat8bppIndexed, sAlgCheckInputParam.vImageData[i].pDATA);
			UINT PaletteSize;
			PaletteSize = bmp.GetPaletteSize();
			Gdiplus::ColorPalette* imgPallet = (Gdiplus::ColorPalette*)malloc(PaletteSize);
			
			Status stImage;
			stImage = bmp.GetPalette(imgPallet, PaletteSize);
			imgPallet->Flags = Gdiplus::PaletteFlags::PaletteFlagsGrayScale;
			for (int i = 0; i < imgPallet->Count; i++) {
				imgPallet->Entries[i] = Color::MakeARGB(0, i, i, i);
			}

			bmp.SetPalette(imgPallet);

			CLSID pngClsid;
			/*
			bmp: {557cf400-1a04-11d3-9a73-0000f81ef32e}
jpg: {557cf401-1a04-11d3-9a73-0000f81ef32e}
gif: {557cf402-1a04-11d3-9a73-0000f81ef32e}
tif: {557cf405-1a04-11d3-9a73-0000f81ef32e}
png: {557cf406-1a04-11d3-9a73-0000f81ef32e}
			*/
			CLSIDFromString(L"{557cf400-1a04-11d3-9a73-0000f81ef32e}", &pngClsid);
			TCHAR FileName[MAX_PATH] = { 0 };
			_snwprintf_s(FileName, MAX_PATH, L"inspid_%d_Page_%d_L_%d.bmp", sAlgCheckInputParam.iInspId, sAlgCheckInputParam.iPageIndex, i);
			PathCombine(FileName, configPath, FileName);
			bmp.Save(FileName, &pngClsid, NULL);
			if (NULL != imgPallet) {
				free(imgPallet);
			}

		}
		else if (sAlgCheckInputParam.vImageData[i].nChannel == 3) {//3：RGB 4:RGBA
			Gdiplus::Bitmap bmp(nImageWidth, nImageHeight, sAlgCheckInputParam.vImageData[i].nPixWidth, PixelFormat24bppRGB, sAlgCheckInputParam.vImageData[i].pDATA);
		}
		else if (sAlgCheckInputParam.vImageData[i].nChannel == 4) {
			Gdiplus::Bitmap bmp(nImageWidth, nImageHeight, sAlgCheckInputParam.vImageData[i].nPixWidth, PixelFormat32bppRGB, sAlgCheckInputParam.vImageData[i].pDATA);
		}
	}

	return true;
}

//参数对话框
s_StatusModelDlg CAlgDarkDefectInspect::CallAlgModelDlg()
{
    s_StatusModelDlg sStatusModelDlg;
    return sStatusModelDlg;
}

//更新参数,根据配置文件信息决定1：加载模板 2：加载参数 ；约束：调用者保证UpdateAlgParam和GCheck串行调用
bool CAlgDarkDefectInspect::UpdateAlgParam()
{
    return true;
}

//系统退出，释放资源
bool CAlgDarkDefectInspect::Free()
{
	GdiplusShutdown(gdiplusToken);
    return true;

}

//获取最后的状态信息
const s_AlgErrorInfo &CAlgDarkDefectInspect::GetLastStatus()
{
    return m_sAlgErrorInfo;

}
