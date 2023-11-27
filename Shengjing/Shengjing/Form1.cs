using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Windows;
using System.Windows.Input;

namespace Shengjing
{
    public partial class Form1 : NForm
    {

        //BackgroundWorker worker = new BackgroundWorker();

        public Form1()
        {
            InitializeComponent();
            GetAllInitInfo(this.Controls[0]);
            Control.CheckForIllegalCrossThreadCalls = false; //加载时 取消跨线程检查

            this.groupBox1.Paint += groupBox_Paint;
            this.groupBox2.Paint += groupBox_Paint;
        }

        //测试进度条控件
        
        

       



        public string main_path = "";
        public string pathname = "";

        string TOF;
        string HSP;
        string HQI;
        string HQO;
        string byear;
        string eyear;
        string begin;
        string end;
        string RP;
        string flag;

        public int statue = 0;
        

        void groupBox_Paint(object sender, PaintEventArgs e)//画groupbox边框
        {
            GroupBox gBox = (GroupBox)sender;

            e.Graphics.Clear(gBox.BackColor);
            e.Graphics.DrawString(gBox.Text, gBox.Font, Brushes.Black, 10, 1);
            var vSize = e.Graphics.MeasureString(gBox.Text, gBox.Font);
            e.Graphics.DrawLine(Pens.Black, 1, vSize.Height / 2, 8, vSize.Height / 2);
            e.Graphics.DrawLine(Pens.Black, vSize.Width + 8, vSize.Height / 2, gBox.Width - 2, vSize.Height / 2);
            e.Graphics.DrawLine(Pens.Black, 1, vSize.Height / 2, 1, gBox.Height - 2);
            e.Graphics.DrawLine(Pens.Black, 1, gBox.Height - 2, gBox.Width - 2, gBox.Height - 2);
            e.Graphics.DrawLine(Pens.Black, gBox.Width - 2, vSize.Height / 2, gBox.Width - 2, gBox.Height - 2);
        }

        private void TestForm_Load(object sender, EventArgs e)
        {

        }

        private void linkLabel1_LinkClicked(object sender, LinkLabelLinkClickedEventArgs e)//文件夹路径选择
        {
            string Path = "";
            FolderBrowserDialog folder = new FolderBrowserDialog();
            folder.Description = "选择文件所在文件夹目录";  //提示的文字
            if (folder.ShowDialog() == DialogResult.OK)
            {
                Path = folder.SelectedPath;
            }
            textBox1.Text = Path + "\\";//后面加\
        }

        private void linkLabel2_LinkClicked(object sender, LinkLabelLinkClickedEventArgs e)
        {
            string Path = "";
            OpenFileDialog dlg = new OpenFileDialog();
            //dlg.Filter = "任意文件(*.*)|*.*";//文件的类型及说明
            dlg.Filter = "Hru文件(*.shp)|*.shp";//文件的类型及说明
            if (dlg.ShowDialog() == DialogResult.OK)//选中确定后
            {
                string filePath = dlg.FileName;
                Path = filePath;
            }
            textBox2 .Text = Path;
        }

        private void linkLabel3_LinkClicked(object sender, LinkLabelLinkClickedEventArgs e)
        {
            string Path = "";
            FolderBrowserDialog folder = new FolderBrowserDialog();
            folder.Description = "选择文件所在文件夹目录";  //提示的文字
            if (folder.ShowDialog() == DialogResult.OK)
            {
                Path = folder.SelectedPath;
            }
            textBox7.Text = Path + "\\";
        }

        private void linkLabel4_LinkClicked(object sender, LinkLabelLinkClickedEventArgs e)
        {
            string Path = "";
            FolderBrowserDialog folder = new FolderBrowserDialog();
            folder.Description = "选择文件所在文件夹目录";  //提示的文字
            if (folder.ShowDialog() == DialogResult.OK)
            {
                Path = folder.SelectedPath;
            }
            textBox8.Text = Path + "\\";
        }

        private void linkLabel5_LinkClicked(object sender, LinkLabelLinkClickedEventArgs e)
        {
            string Path = "";
            FolderBrowserDialog folder = new FolderBrowserDialog();
            folder.Description = "选择文件所在文件夹目录";  //提示的文字
            if (folder.ShowDialog() == DialogResult.OK)
            {
                Path = folder.SelectedPath;
            }
            textBox9.Text = Path + "\\";
        }

        public static string CallCMD(string _command, string _arguments)
        {
            System.Diagnostics.ProcessStartInfo psi = new System.Diagnostics.ProcessStartInfo(_command, _arguments);
            psi.CreateNoWindow = true;
            psi.RedirectStandardOutput = true;
            psi.UseShellExecute = false;
            System.Diagnostics.Process p = System.Diagnostics.Process.Start(psi);


            return (p.StandardOutput.ReadToEnd());
        }
        

        public void bar()
        {
            int flag;
            progressBar1.Visible = true;//设置进度条显示
            //progressBar1.Maximum = 500;//设置最大值
            progressBar1.Value = 0;//设置当前值
            progressBar1.Step = 1;//设置没次增长多少

            if (radioButton1.Checked)//是否画图
            {
                flag = 2;
                progressBar1.Maximum = 200;
            }
            else if (radioButton2.Checked)
            {
                flag = 1;
                progressBar1.Maximum = 750;
            }
            else
            {
                flag = 0;
            }

            for (int i = 0; i < 10000; i++)
            {
                if(progressBar1.Value < progressBar1.Maximum&&statue == 0)
                {
                     
                    if(progressBar1.Value == (progressBar1.Maximum - 1))
                    {
                        progressBar1.Value = (progressBar1.Maximum - 1);
                    }
                    else
                    {
                        Thread.Sleep(1000);
                        progressBar1.Value += progressBar1.Step;
                    }//让进度条增加一次
                }
                else if(statue == 1)
                {
                    progressBar1.Value = progressBar1.Maximum;
                    break;
                }
            }
        }

        public void Threadmain(string TOF, string HSP, string HQI, string HQO, string byear, string eyear, string begin, string end, string RP, string flag)
        {
            string cmdpath = main_path;
            int fin = 0;
            string arg = "" + TOF + "" + " " + "" + HSP + "" + " " + "" + HQI + "" + " " + "" + HQO + "" + " " + "" + byear + "" + " " + "" + eyear + "" + " " + "" + begin + "" + " " + "" + end + "" + " " + "" + RP + "" + " " + "" + flag + "";
            //_cts = new CancellationTokenSource();
            //ThreadPool.QueueUserWorkItem(state => Console.WriteLine(CallCMD(cmdpath, arg)));
            MessageBox.Show("Please wait, it will take about five minutes...", "Wait", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
            richTextBox1.Text = TOF + System.Environment.NewLine + HSP + System.Environment.NewLine + HQI + System.Environment.NewLine + HQO + System.Environment.NewLine + byear + System.Environment.NewLine + eyear + System.Environment.NewLine + begin + System.Environment.NewLine + end + System.Environment.NewLine + RP + System.Environment.NewLine + flag;
            //richTextBox1.Text = richTextBox1.Text + CallCMD(cmdpath, arg);

            Console.WriteLine(CallCMD(cmdpath, arg));
            progressBar1.Value += 1;
            richTextBox1.Text = CallCMD(cmdpath, arg);
            richTextBox1.Text = richTextBox1.Text + System.Environment.NewLine + "Completed!";
            statue = 1;
            progressBar1.Value = progressBar1.Maximum;
            MessageBox.Show("Task Cpmpleted!", "Finished", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
        }

        //测试第二种传参方法
        public void Threadmain1(string TOF, string HSP, string HQI, string HQO, string byear, string eyear, string begin, string end, string RP, string flag)
        {
            string[] strArr = new string[10];//参数列表
            string sArguments = @"main.py";//这里是python的文件名字
            strArr[0] = TOF;
            strArr[1] = HSP;
            strArr[2] = HQI;
            strArr[3] = HQO;
            strArr[4] = byear;
            strArr[5] = eyear;
            strArr[6] = begin;
            strArr[7] = end;
            strArr[8] = RP;
            strArr[9] = flag;
            MessageBox.Show("Please wait, it will take about five minutes...", "Wait", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
            richTextBox1.Text = TOF + System.Environment.NewLine + HSP + System.Environment.NewLine + HQI + System.Environment.NewLine + HQO + System.Environment.NewLine + byear + System.Environment.NewLine + eyear + System.Environment.NewLine + begin + System.Environment.NewLine + end + System.Environment.NewLine + RP + System.Environment.NewLine + flag;
            RunPythonScript(sArguments, "-u", strArr);
            richTextBox1.Text = richTextBox1.Text + System.Environment.NewLine + "Completed!";
            MessageBox.Show("Task Cpmpleted!", "Finished", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
        }

        public static void AppendText(string text)
        {
            Console.WriteLine(text);
        }

        public static void RunPythonScript(string sArgName, string args = "", params string[] teps)
        {
            Process p = new Process();
            string path = System.AppDomain.CurrentDomain.SetupInformation.ApplicationBase + sArgName;// 获得python文件的绝对路径（将文件放在c#的debug文件夹中可以这样操作）
            path = @"C:\Users\hp\Desktop\test_SWAT-DayCent_InVEST\" + sArgName;//(因为我没放debug下，所以直接写的绝对路径,替换掉上面的路径了)
            p.StartInfo.FileName = @"G:\anaconda3\envs\py37\python.exe";//没有配环境变量的话，可以像我这样写python.exe的绝对路径。如果配了，直接写"python.exe"即可
            string sArguments = path;
            foreach (string sigstr in teps)
            {
                sArguments += " " + sigstr;//传递参数
            }

            sArguments += " " + args;

            p.StartInfo.Arguments = sArguments;

            p.StartInfo.UseShellExecute = false;

            p.StartInfo.RedirectStandardOutput = true;

            p.StartInfo.RedirectStandardInput = true;

            p.StartInfo.RedirectStandardError = true;

            p.StartInfo.CreateNoWindow = true;

            p.Start();
            p.BeginOutputReadLine();
            p.OutputDataReceived += new DataReceivedEventHandler(p_OutputDataReceived);
            Console.ReadLine();
            p.WaitForExit();

        }

        static void p_OutputDataReceived(object sender, DataReceivedEventArgs e)
        {
            if (!string.IsNullOrEmpty(e.Data))
            {
                Console.WriteLine(e.Data + Environment.NewLine);
            }

        }

        private void SleepT()
        {
            

            if (textBox1.Text.Contains("\\"))
            {
                textBox1.Text = textBox1.Text.Replace("\\", "/");
            }
            TOF = textBox1.Text;

            if (textBox2.Text.Contains("\\"))
            {
                textBox2.Text = textBox2.Text.Replace("\\", "/");
            }
            HSP = textBox2.Text;

            if (textBox7.Text.Contains("\\"))
            {
                textBox7.Text = textBox7.Text.Replace("\\", "/");
            }
            HQI = textBox7.Text;

            if (textBox8.Text.Contains("\\"))
            {
                textBox8.Text = textBox8.Text.Replace("\\", "/");
            }
            HQO = textBox8.Text;

            if (textBox9.Text.Contains("\\"))
            {
                textBox9.Text = textBox9.Text.Replace("\\", "/");
            }
            RP = textBox9.Text;

            byear = textBox3.Text;
            eyear = textBox5.Text;
            begin = textBox4.Text;
            end = textBox6.Text;

            if (radioButton1.Checked)//是否画图
            {
                flag = "2";
            }
            else if (radioButton2.Checked)
            {
                flag = "1";
            }
            else
            {
                flag = "0";
            }

            Threadmain(TOF, HSP, HQI, HQO, byear, eyear, begin, end, RP, flag);
        }

        private void SleepT2()
        {
            bar();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            string TOF;
            string HSP;
            string HQI;
            string HQO;
            string byear;
            string eyear;
            string begin;
            string end;
            string RP;
            string flag ;

            if (textBox1.Text.Contains("\\"))
            {
                textBox1.Text = textBox1.Text.Replace("\\", "/");
            }
            TOF = textBox1.Text;

            if (textBox2.Text.Contains("\\"))
            {
                textBox2.Text = textBox2.Text.Replace("\\", "/");
            }
            HSP = textBox2.Text;

            if (textBox7.Text.Contains("\\"))
            {
                textBox7.Text = textBox7.Text.Replace("\\", "/");
            }
            HQI = textBox7.Text;

            if (textBox8.Text.Contains("\\"))
            {
                textBox8.Text = textBox8.Text.Replace("\\", "/");
            }
            HQO = textBox8.Text;

            if (textBox9.Text.Contains("\\"))
            {
                textBox9.Text = textBox9.Text.Replace("\\", "/");
            }
            RP = textBox9.Text;

            byear = textBox3.Text;
            eyear = textBox5.Text;
            begin = textBox4.Text;
            end = textBox6.Text;

            if (radioButton1.Checked)//是否画图
            {
                flag = "2";
            }
            else if(radioButton2.Checked)
            {
                flag = "1";
            }
            else
            {
                flag = "0";
            }

            //if (main_path == "")//错误判断
            //{
            //    MessageBox.Show("请选择main.exe路径！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            //}

            if (TOF == "")
            {
                MessageBox.Show("请选择TxtInOut Folder路径！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else if (HSP == "")
            {
                MessageBox.Show("请选择Hru Path路径！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else if (HQI == "")
            {
                MessageBox.Show("请选择HQ_input Folder路径！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else if (HQO == "")
            {
                MessageBox.Show("请选择HQ_output Folder路径！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else if (byear == "")
            {
                MessageBox.Show("请选择开始年份！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else if (eyear == "")
            {
                MessageBox.Show("请选择结束年份！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else if (begin == "")
            {
                MessageBox.Show("请选择预测开始年份！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else if (end == "")
            {
                MessageBox.Show("请选择预测结束年份！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else if (RP == "")
            {
                MessageBox.Show("请选择result结果路径！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else//异步处理
            {
                OpenFileDialog dlg = new OpenFileDialog();
                //dlg.Filter = "任意文件(*.*)|*.*";//文件的类型及说明
                dlg.Filter = "应用程序(*.exe)|*.exe";//文件的类型及说明
                if (dlg.ShowDialog() == DialogResult.OK)//选中确定后
                {
                    string filePath = dlg.FileName;
                    main_path = filePath;
                }
                if (main_path != "")
                {
                    Thread fThread = new Thread(new ThreadStart(SleepT));
                    fThread.Start();
                    Thread fThread2 = new Thread(new ThreadStart(SleepT2));
                    fThread2.Start();
                    progressBar1.Value += 1;
                }
                else
                {
                    MessageBox.Show("请选择main.exe路径！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
                
            }
        }

        //private void button2_Click(object sender, EventArgs e)//选择main.exe
        //{
            
        //    OpenFileDialog dlg = new OpenFileDialog();
        //    //dlg.Filter = "任意文件(*.*)|*.*";//文件的类型及说明
        //    dlg.Filter = "应用程序(*.exe)|*.exe";//文件的类型及说明
        //    if (dlg.ShowDialog() == DialogResult.OK)//选中确定后
        //    {
        //        string filePath = dlg.FileName;
        //        main_path = filePath;
        //    }
        //}

        private void button3_Click(object sender, EventArgs e)
        {
            string outpath = "";
            string pathname = "";
            outpath = textBox9.Text;
            string plot = "";
            //flag = "1";

            if (outpath.Contains("\\"))
            {
                outpath = outpath.Replace("\\", "/");
            }

            if (radioButton1.Checked)//是否画图
            {
                flag = "2";
            }
            else if (radioButton2.Checked)
            {
                flag = "1";
            }
            else
            {
                flag = "0";
            }

            if (flag == "1")//后缀判断
            {
                plot = "动态图.gif";
            }
            else if (flag == "2")
            {
                plot = "静态图.tif";
            }

            pathname = "" + outpath + "" + "2000lulc_100mFigOutput" + "/" + plot;
            
            if (outpath == "")
            {
                MessageBox.Show("请先运行！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else if (flag == "0")
            {
                MessageBox.Show("您未选择画图！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else
            {
                this.pictureBox1.Load(pathname);
            }
        }

        
    }
}


public partial class NForm : Form
{
    #region 控件缩放
    double formWidth;//窗体原始宽度
    double formHeight;//窗体原始高度
    double scaleX;//水平缩放比例
    double scaleY;//垂直缩放比例
    Dictionary<string, string> controlInfo = new Dictionary<string, string>();
    //控件中心Left,Top,控件Width,控件Height,控件字体Size
    /// <summary>
    /// 获取所有原始数据
    /// </summary>
    protected void GetAllInitInfo(Control CrlContainer)
    {
        if (CrlContainer.Parent == this)
        {
            formWidth = Convert.ToDouble(CrlContainer.Width);
            formHeight = Convert.ToDouble(CrlContainer.Height);
        }
        foreach (Control item in CrlContainer.Controls)
        {
            if (item.Name.Trim() != "")
                controlInfo.Add(item.Name, (item.Left + item.Width / 2) + "," + (item.Top + item.Height / 2) + "," + item.Width + "," + item.Height + "," + item.Font.Size);
            if ((item as UserControl) == null && item.Controls.Count > 0)
                GetAllInitInfo(item);
        }
    }
    private void ControlsChangeInit(Control CrlContainer)
    {
        scaleX = (Convert.ToDouble(CrlContainer.Width) / formWidth);
        scaleY = (Convert.ToDouble(CrlContainer.Height) / formHeight);
    }
    private void ControlsChange(Control CrlContainer)
    {
        double[] pos = new double[5];//pos数组保存当前控件中心Left,Top,控件Width,控件Height,控件字体Size
        foreach (Control item in CrlContainer.Controls)
        {
            if (item.Name.Trim() != "")
            {
                if ((item as UserControl) == null && item.Controls.Count > 0)
                    ControlsChange(item);
                string[] strs = controlInfo[item.Name].Split(',');
                for (int j = 0; j < 5; j++)
                {
                    pos[j] = Convert.ToDouble(strs[j]);
                }
                double itemWidth = pos[2] * scaleX;
                double itemHeight = pos[3] * scaleY;
                item.Left = Convert.ToInt32(pos[0] * scaleX - itemWidth / 2);
                item.Top = Convert.ToInt32(pos[1] * scaleY - itemHeight / 2);
                item.Width = Convert.ToInt32(itemWidth);
                item.Height = Convert.ToInt32(itemHeight);
                try
                {
                    item.Font = new Font(item.Font.Name, float.Parse((pos[4] * Math.Min(scaleX, scaleY)).ToString()));
                }
                catch
                {
                }
            }
        }
    }

    #endregion


    protected override void OnSizeChanged(EventArgs e)
    {
        base.OnSizeChanged(e);
        if (controlInfo.Count > 0)
        {
            ControlsChangeInit(this.Controls[0]);
            ControlsChange(this.Controls[0]);
        }
    }
}