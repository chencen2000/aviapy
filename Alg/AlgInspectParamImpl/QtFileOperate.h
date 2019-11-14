
#if !defined(QTFILEOPERATE_H)
#define QTFILEOPERATE_H

#include <QString>
#define WIDTH_BYTES(bits) (((bits) + 31) / 32 * 4)

#pragma execution_character_set("utf-8")

class CQtFileOperate
{

public:
    CQtFileOperate();
    ~CQtFileOperate();

    QString GetLastError();

	// ��ȡ��ִ�г������ڵ�·��
    QString GetCurrentAppPath();


	// �ж�·���Ƿ����
   static bool IsPathExist(QString strPath);
   static bool IsPathExist(std::string strPath);

	//����һ�����Ŀ¼��������ھͲ�����
    static bool CreateMultiLevelPath(QString strPath);
    static bool CreateMultiLevelPath(std::string strPath);
	
	//ɾ����ǰĿ¼�������ļ����ļ���
    bool DeleteDirectory(QString strPath);


    //�����ļ��У�
    //���strToPath�����ڣ��Զ�����strToPath���� ��strFromPath�е����ݣ�������strFromPath����������strToPath��
    //���strToPath���ڣ� ���� false
    bool CopyFolder(QString strFromPath, QString strToPath);


    //������ F:\\Bin\\Model","F:\\Bin\\Model123" ��ʾ��Model������ΪModel123
    bool ReNameFolder(QString strFromPath, QString  strToPath);


	//����Ի���,strInitPath����·��   ���ص��ļ���ȫ·��
    bool BrowseFolder(QString strInitPath, QString &strBrownPath);

    //ɾ��ĳ�ļ����£����¼�֮ǰ���ļ��У����磺F:\Bin\Model\log    ���ļ��и�ʽ2018��08��
    bool DeleteFolderByYearMonDay(QString  strFolder, int iYear, int iMonth, int iDay);
    ///////////////////////////////////////////////////////////////////////////
	//////////////////////////////////////////////////////////////////////////


	//�ж��ļ��Ƿ����
   static bool IsFileExist(QString strFileFullPath);
   static  bool IsFileExist(std::string strFileFullPath);


    bool FileDelete(QString strFileFullPath);


	//strExt = exe����bmp  ����*
    bool FileBrowse(QString strInitPath, QString strExt, QString &strFileFullPath);


	//strExt = exe����bmp  ����*
    bool FileSave(QString strInitPath, QString strExt, QString &strFilePath);

    ///////////////////////////

    static bool MyWritePrivateProfileString(QString strApp, QString strKey, QString strContent,QString strFilePath);
   static QString MyReadPrivateProfileString(QString strApp, QString strKey, QString strDefault, QString strFilePath);

    static bool MyWritePrivateProfileInt(QString strApp, QString strKey, int iContent, QString strFilePath);
   static int MyReadPrivateProfileInt(QString strApp, QString strKey, int iDefault, QString strFilePath);


    static bool MyWritePrivateProfileDouble(QString strApp, QString strKey,  double dbContent, QString strFilePath);
   static double MyReadPrivateProfileDouble(QString strApp, QString strKey, double dbDefault, QString strFilePath);

   static bool MyWritePrivateProfileBool(QString strApp, QString strKey, bool bContent, QString strFilePath);
   static bool MyReadPrivateProfileBool(QString strApp, QString strKey, bool bDefault, QString strFilePath);

    //
   static bool MyWritePrivateProfileString(std::string strApp, std::string strKey, std::string strContent,std::string strFilePath);
   static std::string MyReadPrivateProfileString(std::string strApp, std::string strKey, std::string strDefault, std::string strFilePath);

   static bool MyWritePrivateProfileInt(std::string strApp, std::string strKey, int iContent, std::string strFilePath);
   static int  MyReadPrivateProfileInt(std::string strApp, std::string strKey, int iDefault, std::string strFilePath);


   static bool MyWritePrivateProfileDouble(std::string strApp, std::string strKey,  double dbContent, std::string strFilePath);
   static double MyReadPrivateProfileDouble(std::string strApp, std::string strKey, double dbDefault, std::string strFilePath);

   static bool MyWritePrivateProfileBool(std::string strApp, std::string strKey, bool bContent, std::string strFilePath);
   static bool MyReadPrivateProfileBool(std::string strApp, std::string strKey, bool bDefault, std::string strFilePath);

   //////////////////////////////////////////////////////////////////////////
	//////////////////////////////////////////////////////////////////////////
    //д��־

    bool WriteLog(QString strLogFilePath, QString strContent);
	//////////////////////////////////////////////////////////////////////////
	//////////////////////////////////////////////////////////////////////////

	//����ڴ�ʣ��������������λ��M
     long GetSurplusMemorySize();

	//��õ�ǰӲ�̷�����ʣ��������������-1��ʾʧ�ܵ�λ��M�� ������ D:   E:��
    long GetSurplusCurrentPartitionSize(QString strDrivePath);


	//ɱ����ǰ����
	void ShutCurrentProgcess(); 

	//////////////////////////////////////////////////////////////////////////


	//д������Ϣ
	//�÷� PrintfDebugLog("[PCB]%d starts to run\n", 1);
    static void PrintfDebugLog(const char * strOutputString, ...);
    static void PrintfDebugLog(QString strOutputString);


	//////////////////////////////////////////////////////////////////////////
	//Ҫ��nTextLen = nOutLen��
    bool Encrypt(const char szText[], unsigned int nTextLen, char szOutString[], unsigned int nOutLen);
	bool Decrypt(const char szText[], unsigned int nTextLen, char szOutString[], unsigned int nOutLen);

    QString Encrypt(const QString &strInput);
    QString Decrypt(const QString &strInput);

	//////////////////////////////////////////////////////////////////////////
	//��ͼ��ͼ���ļ���ص�
    bool SaveDIBImageToBMPFile(QString strFileName, const char* pImageBuff, long lImageWidth, long lImageHeight, long lImageBitCount);
    bool CutDIBImage(char *pDest, long xDest, long yDest, long lDestWidth, long lDestHeight, const char* pSrcImageBuff, long lSrcImageWidth, long lSrcImageHeight, long lSrcImageBitCount);
	bool CutPlaneRGBImage(char *pDest, long xDest, long yDest, long lDestWidth, long lDestHeight, const char* pSrcImageBuff, long lSrcImageWidth, long lSrcImageHeight);
	bool ConvertRGBToPlaneR_G_B(char *pDestImageBuffR, char *pDestImageBuffG, char *pDestImageBuffB,
		const char* pSrcImageBuff, long lSrcImageWidth, long lSrcImageHeight);
	bool ConvertPlaneR_G_BToRGB(char* pDestImageBuff, const char *pSrcImageBuffR, const char *pSrcImageBuffG, const char *pSrcImageBuffB,
		long lSrcImageWidth, long lSrcImageHeight);
	bool  ConvertRGBToPlaneRGB(char *pDestPlaneRGBBuff, const char* pSrcImageRGBBuff, long lSrcImageWidth, long lSrcImageHeight);
	bool  ConvertPlaneRGBToRGB(char* pDestImageRGBBuff, const char *pSrcPlaneRGBBuff, long lSrcImageWidth, long lSrcImageHeight);
    static std::string &std_string_format(std::string &_str, const char *_Format...);
    static bool  QTMessageBox(std::string strMessage);
	static std::string GetTimeString();//CH 20190117
private:
     QString m_strErrorInfo;
};





#endif // !define(FileOperate_h_)
